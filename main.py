from flask import Flask, request
import requests
import flask_limiter
import yaml
import subprocess
import os
import time
if not os.path.exists("config/configuration.yml"):
    if os.path.exists("config/default_config.yml"):
        with open("config/default_config.yml", "r") as de:
            with open("config/configuration.yml", "a") as co:
                co.write(de.read())
    else:
        print("🔴 Configuration file not found. Please create a configuration file, or run the setup py (recomended)")
        exit()
    
    print("❗ Configuration file not found. using default config, run the setup py to make a config file")
    
with open("config/configuration.yml","r") as f:
    conf = yaml.load(f,yaml.BaseLoader)

base_service=conf["routing"]["service"]

if base_service=="graphhopper" and 0==2 :
    try: 
        requests.get("http://localhost:8989/health")
    except:
        chop=input("failed to connect to graphhopper do you wanna start it or start it as a service (you only have to start it once this way)? Start / Create service / Exit [s/C/e] ").lower()
        if chop == 'e':
            exit()
        elif chop == 's':
            print("starting graphhoper . . . . this will take some time")
            ff = ""
            for f in os.listdir("graphhoper"):
                if f.endswith(".pbf"):
                    ff = f
            process = subprocess.Popen(
                
                ["java", f"-Ddw.graphhopper.datareader.file={ff}", "-jar", "graphhopper-web-10.0.jar", "server", "config-example.yml"],
                cwd="graphhoper"  # Set the working directory
                )
            while True:
                try:
                    requests.get("localhost:8989/health")
                    print("✅ Started Graphhoper ")
                    break
                except:
                    print("graphhoper not started yet . . .  (if you wish to run graphhoper as a service so you dont have to start it every time you can! visit documentation) ")
                time.sleep(30)
        else:
            pass






import auth


import user_webserver
import delivery_webserver
import admin_webserver


import user_manager as um
import delivery_manager as dm
import order_manager as om


app = Flask("pincer")
app.secret_key = os.urandom(24)
limiter=flask_limiter.Limiter(auth.get_client_ip,app=app)

user_webserver.limiter=limiter
auth.limiter=limiter

app.register_blueprint(user_webserver.app)
app.register_blueprint(delivery_webserver.app)
app.register_blueprint(admin_webserver.app)



def main():    
    app.run(debug=True,host='0.0.0.0',port=8945,use_reloader=False)

if __name__=="__main__":
    main()