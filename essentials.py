import requests

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


