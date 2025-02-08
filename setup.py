import os
import subprocess
import sys
sys.path.append('setup_helper/libs')
import yaml


print("""
      Wwelcome to the pincer setup wizard ! 
      
      """)




# Basic info
def setupconfig():


    print("Basic infos:")
    email = input("Enter an email to be displayed [example@example.com] > ")
    email = email if email != "" else "example@example.com"

    phone = input("Enter a phone number to be displayed [+36 00 000 0000] > ")
    phone = phone if phone != "" else "+36 00 000 0000"

    country_name = input("Enter the country display name you are operating in [Hungary] > ")
    country_name = country_name if country_name != "" else "Hungary"

    country_code = input("Enter the country's two-character code you are operating in [HU] > ")
    country_code = country_code if country_code != "" else "HU"

    currency = input("Enter a currency to be displayed [HUF] > ")
    currency = currency if currency != "" else "HUF"


    # Database info
    print("\nDatabase infos:")
    dbtype = input("What database do you want to use? Sqlite or mysql (you need to have a server!) [SQLITE/mysql] > ")
    if dbtype.lower() == "mysql":
        dbhost = input("Enter the mysql host [localhost] > ")
        dbhost = dbhost if dbhost != "" else "localhost"
        dbuser = input("Enter the mysql user > ")
        dbpass = input("Enter the mysql password > ")
        dbname = input("Enter the mysql database name > ")
    else:
        dbtype="sqlite"

    # Routing info
    print("\nRouting infos:")
    print("This is used for routing the delivery men.")
    print("You can use the following routing types:")
    print("1. Auto-setup graphhopper (self-hosted, free, and open-source routing tool)")
    print("2. Openrouteservice API (you need to register a free account at https://openrouteservice.org/)")
    print("3. Manually install graphhopper later")
    print("4. Set up your own later (you have to modify the routing.py)")
    print("recommended: 1")

    routeservice=input(" > ")

    while not routeservice in ("1", "2", "3", "4"):
        routeservice=input(" > ")

        print("Enter 1, 2, 3, or 4")
    if routeservice == "2":
        api_key=input("you api key > ")
    else:
        api_key=""
    if routeservice == "1":
        country_location = input("region osm file download path ( ususally /continent/country/city or /continent/country if you want the whole country ) [/europe/hungary] > ")
        if country_location == "":
            country_location = "/europe/hungary"

    # Auth info
    print("\nAuth infos:")
    admin_password = input("Enter an admin password for accessing the admin page [mester00] > ")
    google_auth = input("Do you want Google authentication? [yes/NO] > ")

    if google_auth.lower() == "yes":
        print("Please set up Google authentication at https://console.cloud.google.com/")
        auth_id = input("Your auth client ID (you can go back with BACK) > ")
        if auth_id.lower() == "back":
            auth_id = ""
        else:
            auth_secret = input("Your Google auth client secret > ")
            redirect_url = input("Your Google auth client redirect URL (http or https://your-server-ip:port-or-domain/auth/callback) > ")
    else:
        auth_id = ""
        auth_secret = ""
        redirect_url = ""

    # Prepare YAML content
    config = {
        "basic_infos": {
            "phone": phone,
            "email": email,
            "country": country_name,
            "country_code": country_code,
            "currency": currency
        },
        "database_infos": {
            "type": dbtype.lower(),
            "host": dbhost if dbtype.lower() == "mysql" else "",
            "user": dbuser if dbtype.lower() == "mysql" else "",
            "password": dbpass if dbtype.lower() == "mysql" else "",
            "database": dbname if dbtype.lower() == "mysql" else "pincer"
        },
        "routing": {
            "service": {"1":"graphhopper","2":"openroutingservice","3":"graphhopper","4":"manual"}[routeservice],
            "api_key": api_key
        },
        "auth": {
            "admin_password": admin_password,
            "google_CLIENT_ID": auth_id,
            "google_CLIENT_SECRET": auth_secret if google_auth.lower() == "yes" else "",
            "google_REDIRECT_URI": redirect_url if google_auth.lower() == "yes" else ""
        },
        "session_config": {
            "session_idle_timeout": "60*30",
            "max_timeout": "60*60*3"
        },
        "delivery_session_config": {
            "session_idle_timeout": "60*10",
            "max_timeout": "60*60*5"
        }
    }

    # Save configuration to YAML file
    with open("config/configuration.yml", "w") as file:
        yaml.dump(config, file, default_flow_style=False)

    print("Configuration saved to config/configuration.yml")

    print(config)
    return config, int(routeservice), dbtype, "", "", "", country_location




import time

def setup():

    #setupp = input("Do you want to setup via a web GUI or via terminal? [web/TER] > ")

    #if setupp.lower() == "web":
    #    import setup_helper.web
    #    setup_helper.web.start()
    #
    #    input("")
    #else:
    #    pass
    conffile()
    
    ###### the magic
    
    print("\n\n Sit back and relax until the first error :)")
    time.sleep(1)


def conffile():

    print("\nSetting up configuration\n")

    if os.path.exists("config/configuration.yml"):
        if input("configuration file already exist do you want to reconfigure? (y/N) > ") == "y":
            conf, routeservice, dbtype, dbhost, dbname, dbuser, location  = setupconfig()

        else:
            with open("config/configuration.yml","r") as f:
                conf = yaml.load(f,yaml.BaseLoader)
                routeservice=0
                country_location = input("region osm file download path ( ususally /continent/country/city or /continent/country if you want the whole country ) [/europe/hungary] > ")
                if country_location == "":
                    country_location = "/europe/hungary"
                location = country_location
    else:
        conf, routeservice, dbtype, dbhost, dbname, dbuser, location  = setupconfig()

    req()
    graph(location)
    database()











def req():

    print("\ninstalling requiremnts . . . . ")
    time.sleep(1)

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("\n✅ Installed requirements sucessfully! \n\n")
    except subprocess.CalledProcessError as e:
        print("\n❌ failed to install the requiremts!")
        print("\n\nPlease install the requirements in the requirements.txt manually (pip install -r requirements.txt)\n")
        if not input("did you already installed them? [yes/NO] > ") == "yes":
            exit()



def graph(location):

        print("installing Graphhoper . . . . ")
        time.sleep(1)
        
        directory = "graphhoper"
        
        if not os.path.exists(directory):
            os.mkdir(directory)

        try:
            subprocess.check_call([
                "wget", "-P", directory, "https://repo1.maven.org/maven2/com/graphhopper/graphhopper-web/10.0/graphhopper-web-10.0.jar",
                "https://raw.githubusercontent.com/graphhopper/graphhopper/10.x/config-example.yml",
            ])
            print("\n✅ Installed Graphhoper sucessfully! \n\n")
            print("downloading map data . . . .")
            time.sleep(0.5)
            try:
                subprocess.check_call([
                "wget", "-P", directory, f"http://download.geofabrik.de/{location}-latest.osm.pbf"])
                print("\n✅ Downloaded map data sucessfully! \n\n")
            except:
                print("\n❌ failed to download the map data!")
            
            print("testing graphhoper . . . . ")
            time.sleep(0.5)
            try:
                process = subprocess.Popen(['java', f'-Ddw.graphhopper.datareader.file={location.split("/")[-1]}-latest.osm.pbf', '-jar', 'graphhopper-web-10.0.jar', 'server', 'config-example.yml'],cwd="graphhoper")
                while True:
                    if process.poll() is not None:
                        print("\n❌ failed to start graphhoper!")
                        break
                    import requests
                    response = requests.get('http://localhost:8989/health')
                    if response.status_code == 200:
                        print("\n\n\n✅ Graphhoper is working sucessfully! \n\n")
                        
                        process.terminate()
                        process.wait()

                        break
                    time.sleep(1)
            except:
                print("\n❌ failed to start graphhoper!")
        except:
            print("\n❌ failed to download the Graphhoper!")

def database():


    print("setting up the database structure . . . . ")    
    try:
        import database
    except:
        print("\n❌ failed to import the database module!")




do = input("what do you wanna do? Complete setup, Reconfigure, Install requirements, setup Grapphoper, setup the Database? [C/r/i/g/d] > ")
if do.lower() == "i":
    req()
elif do.lower() == "g":
    country_location = input("region osm file download path ( ususally /continent/country/city or /continent/country if you want the whole country ) [/europe/hungary] > ")
    if country_location == "":
        country_location = "/europe/hungary"
    graph(country_location)
elif do.lower() == "d":
    database()
elif do.lower() == "r":
    setupconfig()
else:
    conffile()  # Complete setup