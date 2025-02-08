from flask import Flask, jsonify, request
import flask
import flask_limiter
import json
import yaml
import requests
import time
import random
import os
from essentials import get_country_code_by_ip, reverse_geocode, is_coordinates_in_hungary

import auth

import sessions_manager as sm
import user_manager as um
import order_manager as om

app = flask.Blueprint('user_webserver', __name__)
app.secret_key = os.urandom(24)

app.register_blueprint(auth.app)

limiter=None

with open("config/configuration.yml","r") as f:
    conf = yaml.load(f,yaml.BaseLoader)

COUNTRY_NAME=conf["basic_infos"]["country"]
COUNTRY_CODE=conf["basic_infos"]["country_code"]


GUEST_ICON = "/static/images/guest.jpg"


with open("config/configuration.yml","r") as f:
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
    token=request.cookies.get("sessiontoken")
    user=sm.getbytoken(token)
    if not user:
        return "redirect to login",304
        
    if not user.user:
        return "please login agin",304


    price=get_price(foodname,rest)
    html=f"<h1>{foodname}</h1>\n<a>{price}Ft</a><br>\n<h3>Hogy szeretnéd?</h2>\n"

    with open(f"data/{rest}_menu.json") as f:
        data=json.load(f)
    foodlist={}
    for d in data:
        foodlist[d["name"]] = d

    food=foodlist[foodname]

    options=food["options"]

    for option in options:
        if option["type"] == "choice":
            radioGroup=option["name"]
            html+=f"""<label class="potitle">{option["name"]}</label>"""
            for index,choice in enumerate(option["options"]):
                html+=f"""<input type="radio" id="option-{radioGroup}-{index}" name="{radioGroup}" value="{choice}">
                <label for="option-{radioGroup}-{index}">{choice}</label>"""
                

        if option["type"] == "checkbox":
            index=random.randint(1000,9999)
            html+=f"""<input type="checkbox" id="check{index}">
                <label for="check{index}">{option["name"]}</label>"""

        html+= "\n<br>\n"

    html+=f"\n<button onClick='document.getElementById(\"popup\").classList.remove(\"visible\")'>Back</button> <button onClick='selected(\"{rest}\",\"{foodname}\")'>OK</button>"

    return html

@app.route("/placeorderpart/<resta>/<food>",methods=["POST"])
def placeorderpart(resta,food):

    token=request.cookies.get("sessiontoken")

    user=sm.getbytoken(token)

    if not user:
        return "redirect to login",304
        
    if not user.user:
        return "please login agin",304
    user=user.user


    data=request.data
    data=json.loads(data)

    if user.data.get("basket"):
        if user.data["basket"].get(resta):
            user.data["basket"][resta].append({"item":food,"modifications":data})
        else:
            user.data["basket"][resta]= [{"item":food,"modifications":data}]
    else:
        user.data["basket"]={resta:[{"item":food,"modifications":data}]}

    user.save()  # important to save after any changes (this writes back to the db) else the chanching is only in cashe

    return "ok",200

@app.route("/getbasketcount/<resta>")
def getbasketcount(resta):
    token=request.cookies.get("sessiontoken")
    user=sm.getbytoken(token)
    if user:
        user=user.user
        if user.data.get("basket"):
            if user.data["basket"].get(resta):
                return str(len(user.data["basket"][resta]))
            else:
                return "0"
        else:
            return "0"
    else:
        return "0"

@app.route("/getbasket/<resta>")
def getbasket(resta):
    token = request.cookies.get("sessiontoken")
    user = sm.getbytoken(token)
    if user:
        user = user.user
        if user.data.get("basket"):
            if user.data["basket"].get(resta):
                basket = user.data["basket"][resta]
                price=cacl_price(user.data["basket"],resta)
                html = f"<h1>{resta} order:</h1>\n<a>{price}Ft</a>"
                for item in basket:
                    html += f"<h2>{item['item']}  ({get_price(item["item"],resta)}Ft)</h2>"
                    for mod in item["modifications"]["choices"].keys():
                        html += f"<a>{mod}:{item['modifications']['choices'][mod]}, </a>"
                    for mod in item["modifications"]["extras"]:
                        html += f"<a>{mod}, </a>"
                    html += "<br>"    
            
                html += f"\n <button onClick='resetbasket(\"{resta}\")'>Restart</button> <button onClick='document.getElementById(\"basket\").classList.remove(\"visible\")'>Back</button> <button onClick=\"confirmorder(\'{resta}\')\">Confirm</button>"
                return html
            else:
                return "empty basket <button onClick='document.getElementById(\"basket\").classList.remove(\"visible\")'>Back</button>"
        else:
            return "empty basket <button onClick='document.getElementById(\"basket\").classList.remove(\"visible\")'>Back</button>"
    else:
        return flask.redirect("/login?redirect=/restaurant/"+resta)


@app.route("/resetbasket/<resta>")
def resetbasket(resta):
    token = request.cookies.get("sessiontoken")
    user = sm.getbytoken(token)
    if user:
        user = user.user
        if user.data.get("basket"):
            if user.data["basket"].get(resta):
                del user.data["basket"][resta]
                user.save()
                return "basket reset"
            else:
                return "empty basket",400
        else:
            return "empty basket",400
    else:
        return flask.redirect("/login?redirect=/restaurant/"+resta)


@app.route("/confirmorder/<resta>")
def confirmorder(resta):
    token = request.cookies.get("sessiontoken")
    user = sm.getbytoken(token)
    if user:
        user = user.user
        if user.data.get("basket"):
            if user.data["basket"].get(resta):
                user.data["selectedrestaurant"]=resta
                user.save()
                return flask.redirect("/order")
            else:
                return "you have nothing in you basket",400
        else:
            return "you have nothing in you basket",400
    else:
        return flask.redirect("/login?redirect=/restaurant/"+resta)
            

@app.route("/order")
def order():

    token = request.cookies.get("sessiontoken")
    user = sm.getbytoken(token)
    if user:
        user = user.user
        if user.data.get("selectedrestaurant"):
            price=cacl_price(user.data["basket"],user.data["selectedrestaurant"])
            html=""
            for food in user.data["basket"][user.data["selectedrestaurant"]]:
                pr=get_price(food["item"],user.data["selectedrestaurant"])
                html+=food["item"]+" ("+str(pr)+"Ft);        "
            return flask.render_template("order.html",basket=html,price=price,restaurant=user.data["selectedrestaurant"],pfpurl=user.profilepicture)
        else:
            return flask.redirect("/restaurants")
    else:
        return flask.redirect("/login?redirect=/order")


def cacl_price(basket,restaurant):
    price=0
    for order in basket[restaurant]:
        with open(f"data/{restaurant}_menu.json") as f:
            data=json.load(f)
        foodlist={}
        for item in data:
            foodlist[item["name"]] = item
        price+=foodlist[order["item"]]["price"]
    return price

def get_price(item_name,restaurant):
    with open(f"data/{restaurant}_menu.json") as f:
        data=json.load(f)
    foodlist={}
    for item in data:
        foodlist[item["name"]] = item
    return foodlist[item_name]["price"]


@app.route("/confirmlocation",methods=["POST"])
def confirmlocation():
    token = request.cookies.get("sessiontoken")
    user = sm.getbytoken(token)
    if user:
        user = user.user
        data=json.loads(request.data)
        location=data.get("search")
        hn = data.get("hn")
        user.data["location"]={"location":location,"hn":hn}
        cords=reverse_geocode(location)
        if not is_coordinates_in_hungary(lat=cords[0],lon=cords[1]):
            return f"You are not in {COUNTRY_NAME}; you cant order to outside the country yet",400
        if not get_country_code_by_ip(request.headers.get('X-Forwarded-For', request.remote_addr)) == COUNTRY_CODE:
            return f"You are not in {COUNTRY_NAME}; you cant order from outside the country, this may happened bc you use a vpn",400
        user.save()
        return "ok",200
    else:
        return flask.redirect("/login?redirect=/order")

@app.route("/payment")
def payment():
    token = request.cookies.get("sessiontoken")
    user = sm.getbytoken(token)
    if user:
        user = user.user
        if user.data.get("location"):
            price=cacl_price(user.data["basket"],user.data["selectedrestaurant"])
            return flask.render_template("payment.html",price=price,pfpurl=user.profilepicture)
        else:
            return flask.redirect("/order")
    else:
        return flask.redirect("/login?redirect=/order")
    

@app.route("/dopayment",methods=["POST"])
def dopayment():
    token = request.cookies.get("sessiontoken")
    user = sm.getbytoken(token)
    if user:
        user = user.user
        if user.data.get("location"):

            
            #user.data["order"] = {"status":"ordered","time":time.time(),"location":user.data["location"],"basket":user.data["basket"][user.data["selectedrestaurant"]],"restaurant":user.data["selectedrestaurant"],"price":cacl_price(user.data["basket"],user.data["selectedrestaurant"])}
            order=om.make_oreder(user.id,user.data["basket"][user.data["selectedrestaurant"]],user.data["selectedrestaurant"],user.data["location"],cacl_price(user.data["basket"],user.data["selectedrestaurant"]))
            order.fulfill()

            del user.data["basket"][user.data["selectedrestaurant"]]
            del user.data["selectedrestaurant"]
            user.save()

            return "ok",200
           
        else:
            return "missing data",400
    else:
        return flask.redirect("/login?redirect=/order")


@app.route("/track-order")
def trackorder():
    token = request.cookies.get("sessiontoken")
    user = sm.getbytoken(token)
    if user:
        user = user.user
        orders=om.get_orders(user.id)
        ret=[]
        for order in orders:
            ret.append(order.json())
        
        return flask.render_template("track-order.html",segments=ret,pfpurl=user.profilepicture)
    else:
        return flask.redirect("/login?redirect=/track-order")

@app.route("/track-order/<id>")
def trackorder(id):
    token=request.cookies.get("sessiontoken")
    ses=sm.getbytoken(token)
    if ses:
        user=ses.user
        orders=om.get_orders(user.id)
        req=om.get(id)
        if not req:
            return flask.redirect("/track-order")
        if not req in orders:
            return flask.redirect("/track-order")
        


@app.errorhandler(500)
def error(e):
    return jsonify({"code":500,"message":"something went wrong"}),500

@app.errorhandler(404)
def notfound(e):
    an = flask.make_response(flask.redirect("/"))
    an.set_cookie("notfound", "yes")
    return an
