from flask import Flask, jsonify, request
import flask
import flask_limiter
import json
import yaml
import requests
import time
import random
import os
from essentials import get_country_code_by_ip

import auth

import sessions_manager as sm
import user_manager as um

app = Flask("user_webserver")
app.secret_key = os.urandom(24)

app.register_blueprint(auth.app)

limiter=flask_limiter.Limiter(auth.get_client_ip,app=app)

auth.limiter=limiter

GUEST_ICON = "https://tse3.mm.bing.net/th?id=OIP.qcjhP7DA8HG_kIRvZDoDvQHaHa&pid=Api&P=0&h=220"

with open("data/configuration.yml","r") as f:
    conf = yaml.load(f,yaml.BaseLoader)
    
PHONE=conf["basic_infos"]["phone"]
EMAIL=conf["basic_infos"]["email"]




@app.route("/favicon.ico")
def favicon():
    return flask.send_file("static/images/logo.ico")


@app.route('/')
def indexx():
    token=request.cookies.get("sessiontoken")
    nff=request.cookies.get("notfound")
    nf=False
    if nff:
        if nff=="yes":
            nf=True
    if token:
        if sm.getbytoken(token):
            pfpurl=sm.getbytoken(token).user.profilepicture
        else:
            pfpurl=GUEST_ICON
    else:
        pfpurl=GUEST_ICON
 
    an=flask.make_response(flask.render_template('home.html' if not nf else 'home_nf.html', nf=nf,pfpurl=pfpurl,country=get_country_code_by_ip(request.headers.get('X-Forwarded-For', request.remote_addr))))
    if nf:
        an.delete_cookie("notfound")
    return an


@app.route("/restaurant/<name>")
def restaurant(name):
    token=request.cookies.get("sessiontoken")
    if token:
        user=sm.getbytoken(token)
        if user:
            pfp=user.user.profilepicture
        else:
            pfp=GUEST_ICON
    else:
        pfp=GUEST_ICON
    reli={}
    with open("data/restaurants.json") as jon:
        restaurants=json.load(jon)
        for resi in restaurants:
            reli[resi["name"]] = resi

    if not name in reli:
        return flask.redirect("/restaurants")

    with open(f"data/{name}_menu.json") as f:
        menu=json.load(f)
        segments=menu

    return flask.render_template('foods.html', segments=segments, pfpurl=pfp, restaurant=name)


@app.route("/phone")
def phone():
    return flask.render_template("phone_home.html")


@app.route("/login")
def loginsite():
    token=request.cookies.get("sessiontoken")
    if token:
        if sm.getbytoken(token):
            return flask.redirect("/profile")
    redirect=request.args.get("redirect")
    if redirect:
        resp = flask.make_response(flask.redirect("/login"))
        resp.set_cookie("redirect", redirect)
        return resp
    return flask.render_template("login.html")


@app.route("/profile")
def profile():
    token=request.cookies.get("sessiontoken")
    if token:
        if sm.getbytoken(token):
            user=sm.getbytoken(token).user
            return flask.render_template("profile.html",pfpurl=user.profilepicture,username=user.name,email=user.email)
        else:
            return flask.redirect("/login")
    else:
        return flask.redirect("/login")
    

@app.route("/contact")
def contact():
    user=sm.getbytoken(request.cookies.get("sessiontoken"))
    return flask.render_template("contact.html",email=EMAIL,phone=PHONE,pfpurl=user.user.profilepicture if user else GUEST_ICON)


@app.route("/about")
def aboutus():
    user=sm.getbytoken(request.cookies.get("sessiontoken"))
    return flask.render_template("us.html",pfpurl=user.user.profilepicture if user else GUEST_ICON)


@app.route('/restaurants')
def dashboard():
    token=request.cookies.get("sessiontoken")
    if token:
        if sm.getbytoken(token):
            pfpurl=sm.getbytoken(token).user.profilepicture
        else:
            pfpurl=GUEST_ICON
    else:
        pfpurl=GUEST_ICON

    with open("data/restaurants.json") as jon:
        restaurants=json.load(jon)
        segments=restaurants

    return flask.render_template('dashboard.html', segments=segments, pfpurl=pfpurl)

@app.route("/foodinfo/<rest>/<foodname>")
def foodinfo(rest,foodname):

    html=""

    with open(f"data/{rest}_menu.json") as f:
        data=json.load(f)
    foodlist={}
    for d in data:
        foodlist[d["name"]] = d

    food=foodlist[foodname]

    options=food["options"]

    for option in options:
        if option["type"] == "choice":
            radioGroup=random.randint(1000,9999)
            html+=f"""<label class="popup-content">{option["name"]}</label>"""
            for index,choice in enumerate(option["options"]):
                html+=f"""<input class="popup-content" type="radio" id="option-{radioGroup}-{index}" name="{radioGroup}" value="{choice}">
                <label for="option-{radioGroup}-{index}">{choice}</label>"""
                

        if option["type"] == "checkbox":
            index=random.randint(1000,9999)
            html+=f"""<input type="checkbox" id="check{index}">
                <label for="check{index}">{option["name"]}</label>"""

        html+= "\n<br>\n"

    return html


@app.errorhandler(500)
def error(e):
    return jsonify({"code":500,"message":"something went wrong"}),500

@app.errorhandler(404)
def notfound(e):
    an = flask.make_response(flask.redirect("/"))
    an.set_cookie("notfound", "yes")
    return an

      
def main():    
    app.run(debug=True,host='0.0.0.0',port=8945)

if __name__=="__main__":
    main()