from flask import Flask, request
import flask_limiter
import os
import time

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