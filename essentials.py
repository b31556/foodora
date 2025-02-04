import requests
import math
import polyline  # Install the polyline package with pip if needed

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
        # Ha több IP van, az első a kliens IP
        print(forwarded_for.split(",")[0].strip())
        return forwarded_for.split(",")[0].strip()
    print(request.remote_addr)
    return request.remote_addr


def is_coordinates_in_hungary(lat: float, lon: float) -> bool:
    # Hungary's approximate bounding box
    min_lat, max_lat = 45.74, 48.58  # South to North
    min_lon, max_lon = 16.11, 22.90  # West to East
    
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon

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
    headers = {"User-Agent": "MyPythonApp/1.0 (contact@example.com)"}
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


def get_route(from_lat, from_long, to_lat, to_long):
    # GraphHopper API URL
    url = f"http://localhost:8989/route?point={from_lat},{from_long}&point={to_lat},{to_long}&profile=car&locale=en"

    try:
        # Sending GET request to the GraphHopper API
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response JSON
        data = response.json()

        # Decode the polyline points
        encoded_points = data['paths'][0]['points']
        decoded_points = polyline.decode(encoded_points)
        new_dec=[]
        for desc in decoded_points:
            new_dec.append([desc[0],desc[1]])

        # Extract relevant information
        route_info = {
            "points": new_dec,  # Decoded points as a list of (lat, lon) tuples
            "distance": data['paths'][0]['distance'],  # in meters
            "time": data['paths'][0]['time'],          # in milliseconds
            "instructions": [instruction['text'] for instruction in data['paths'][0]['instructions']],
            "bbox": data['paths'][0]['bbox'],          # Bounding box of the route
            "road_data_timestamp": data['info']['road_data_timestamp'],
            "visited_nodes": data['hints']['visited_nodes.average'],
        }

        return route_info
    
    except requests.exceptions.RequestException as e:
        print(f"Error with the request: {e}")
        return None
    except KeyError as e:
        print(f"Error processing the response: Missing key {e}")
        return None


