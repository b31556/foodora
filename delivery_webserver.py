from flask import Flask,Blueprint, render_template, request, redirect, url_for, jsonify, send_file, make_response, render_template
from flask_limiter import Limiter, RateLimitExceeded
import requests
import random
import time
import json
from database import read_database, write_database

from essentials import is_coordinates_in_hungary, get_country_code_by_ip, get_route

def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", None)
    if forwarded_for:
        # Ha több IP van, az első a kliens IP
        print(forwarded_for.split(",")[0].strip())
        return forwarded_for.split(",")[0].strip()
    print(request.remote_addr)
    return request.remote_addr

import order_manager as om
import delivery_manager as dm
import delivery_session_manager as sm

app = Blueprint('delivery', __name__, url_prefix='/delivery')

@app.route("/")
def index():
    return render_template("delivery/index.html")



@app.route("/api/register", methods=["POST"])
def register():
    data=request.json
    name = data.get("name")
    passw = data.get("passw")
    email = data.get("email")
    vehicle = data.get("vehicle")
    lat = data.get("lat")
    long = data.get("long")
    profilepic = data.get("profilepic")
     
    if name and passw and email and vehicle and lat and long:
        if vehicle not in ["car","motor","bicycle","foot","robogo"]:
            return "Invalid vehicle type", 400
        if dm.getbyemail(email):
            return "Email already in use", 400
        if not is_coordinates_in_hungary(float(lat),float(long)):
            return "Coordinates not in Hungary", 400
        if get_country_code_by_ip(get_client_ip())!="HU":
            return "IP not from Hungary", 400
        user = dm.make(name, passw, email, vehicle, {"lat":float(lat),"long":float(long)}, profilepic)
        return f"{sm.make(user).token}&{user.token}",200
    else:
        return "Missing data", 400


@app.route("/api/login", methods=["POST"])
def login():
    data=request.json
    email = data.get("email")
    passw = data.get("passw")
    if email and passw:
        user = dm.getbyemail(email)
        if user and user.passw==passw:
            return f"{sm.make(user).token}&{user.token}",200
        else:
            return "Invalid email or password", 400
    else:
        return "Missing data", 400

@app.route("/api/tokenlogin", methods=["POST"])
def tokenlogin():
    data=request.json
    token = data.get("token")
    if token:
        user = dm.getbytoken(token)
        if user:
            return f"{sm.make(user).token}&{user.token}",200
        else:
            return "Invalid token", 401
    else:
        return "Missing data", 401

@app.route("/api/logout", methods=["POST"])
def logout():
    data=request.json
    token = data.get("token")
    if token:
        session = sm.getbytoken(token)
        if session:
            session.delete()
            return "Logged out",201
        else:
            return "Invalid token", 401
    else:
        return "Missing data", 401

@app.route("/api/report", methods=["POST"])
def test():
    data=request.json
    token = data.get("token")
    lat = data.get("lat")
    long = data.get("long")
    command = data.get("command")
    if token and lat and long:
        session = sm.getbytoken(token)
        if session:
            user = session.user
            user.position = {"lat":float(lat),"long":float(long)}
            if command:
                if command == "online":
                    user.online = True
                elif command == "offline":
                    user.online = False

            route=get_route(user.position["lat"],user.position["long"],user.destination["lat"],user.destination["long"])
            print(f"sent a query with {user.position['lat']},{user.position['long']} and {user.destination['lat']},{user.destination['long']}")
            return json.dumps({"route":route,"destination":{"lat":user.destination["lat"], "long":user.destination["long"]},"online":"Várakozás a feladat kiosztására" if user.online and user.inprogress_order == "" else "Nem vagy elérhető" if user.inprogress_order == "" else f"Deliverying from a {om.get(user.inprogress_order).restaurant}"}),210
        else:
            return "Invalid token", 401
    else:
        return "Missing data", 401


