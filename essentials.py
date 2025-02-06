import requests
import math
import polyline
import yaml

with open("config/configuration.yml","r") as f:
    conf = yaml.load(f,yaml.BaseLoader)

base_service=conf["routing"]["service"]
base_api_key=conf["routing"]["api_key"]



def get_country_code_by_ip(ip_address):
    try:
        url = f"http://ip-api.com/json/{ip_address}"
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "success":
             return data["countryCode"]
        else:
            return f"Error: {data['message']}"
    except Exception as e:
        return f"Exception occurred: {e}"
    

def get_client_ip(request):
    forwarded_for = request.headers.get("X-Forwarded-For", None)
    if forwarded_for:
        print(forwarded_for.split(",")[0].strip())
        return forwarded_for.split(",")[0].strip()
    print(request.remote_addr)
    return request.remote_addr


def is_coordinates_in_hungary(lat: float, lon: float) -> bool:
    # Hungary's approximate bounding box
    min_lat, max_lat = 45.74, 48.58  # South to North
    min_lon, max_lon = 16.11, 22.90  # West to East
    
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def get_place_by_coordinates(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json"
    head={"User-Agent":"Mypython-app/1.0"}
    response = requests.get(url,headers=head)
    data = response.json()
    
    if 'address' in data:
        return f"{data['address']['road']}, {data['address']['town']}"
    else:
        return "Location not found"


def haversine(lat1, lon1, lat2, lon2):
    # Föld sugara km-ben
    R = 6371.0  

    # Koordináták átváltása radiánba
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Különbségek kiszámítása
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine-képlet
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Távolság kiszámítása
    distance = R * c  
    return distance

def reverse_geocode(location_name):
    url = "https://nominatim.openstreetmap.org/search"

    headers = {"User-Agent": "Pincer_PythonApp/1.0 (tbguru558@gmail.com)"}
    params = {"q": location_name, "format": "json"}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if data:
        lat, lon = float(data[0]["lat"]), float(data[0]["lon"])
        return lat, lon
    else:
        return None  # Ha nincs találat

def chose_best_delivery_man(list, location):
    lat,long = reverse_geocode(location)
    best=None
    best_dist=999999999999
    for man in list:
        if man.inprogress_order=="" and man.online: # ha nincs éppen szállításban
            dist=haversine(man.position["lat"],man.position["long"],lat,long)
            if dist<best_dist:
                best=man
                best_dist=dist
    return best


def get_route(from_lat, from_long, to_lat, to_long, service=base_service, api_key=base_api_key):
    if service == "graphhopper":
        url = f"http://localhost:8989/route?point={from_lat},{from_long}&point={to_lat},{to_long}&profile=car&locale=en"
    elif service == "openrouteservice":
        url = f"https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {"Authorization": api_key, "Content-Type": "application/json"}
        payload = {
            "coordinates": [[from_long, from_lat], [to_long, to_lat]],  # OpenRouteService uses [lon, lat] format
            "instructions": "true"
        }
    else:
        print("Invalid service specified")
        return None

    try:
        if service == "graphhopper":
            response = requests.get(url)
        else:  # openrouteservice
            response = requests.post(url, json=payload, headers=headers)

        response.raise_for_status()
        data = response.json()

        if service == "graphhopper":
            encoded_points = data['paths'][0]['points']
            decoded_points = polyline.decode(encoded_points)
            route_info = {
                "points": [[lat, lon] for lat, lon in decoded_points],
                "distance": data['paths'][0]['distance'],
                "time": data['paths'][0]['time'],
                "instructions": [instr['text'] for instr in data['paths'][0]['instructions']],
                "bbox": data['paths'][0]['bbox'],
                "road_data_timestamp": data['info']['road_data_timestamp'],
                "visited_nodes": data['hints']['visited_nodes.average'],
            }
        else:  # openrouteservice
            encoded_points = data['routes'][0]['geometry']
            decoded_points = polyline.decode(encoded_points)
            route_info = {
                "points": [[lat, lon] for lat, lon in decoded_points],
                "distance": data['routes'][0]['summary']['distance'],
                "time": data['routes'][0]['summary']['duration'] * 1000,  # Convert to ms
                "instructions": [instr['instruction'] for instr in data['routes'][0]['segments'][0]['steps']],
                "bbox": data['routes'][0]['bbox'],
            }

        return route_info

    except requests.exceptions.RequestException as e:
        print(f"Error with the request: {e}")
        return None
    except KeyError as e:
        print(f"Error processing the response: Missing key {e}")
        return None



