from flask import Flask
import flask_limiter
import os
from auth import get_client_ip


import user_webserver
import delivery_webserver


import user_manager as um
import delivery_manager as dm


app = Flask("pincer")
app.secret_key = os.urandom(24)
limiter=flask_limiter.Limiter(get_client_ip,app=app)

user_webserver.limiter=limiter

app.register_blueprint(user_webserver.app)
app.register_blueprint(delivery_webserver.app)

@app.route("/reload")
def reload():
    um.logged_in_users={}
    dm.logged_in_users={}
    return "cache deleted"


def main():    
    app.run(debug=True,host='0.0.0.0',port=8945,use_reloader=False)

if __name__=="__main__":
    main()