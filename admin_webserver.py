import flask
import time
import json
import yaml
import essentials
import random

import user_manager as um
import delivery_manager as dm
import order_manager as om

import sessions_manager as sm
import delivery_session_manager as dsm

with open("config/configuration.yml","r") as f:
    conf = yaml.load(f,yaml.BaseLoader)

MESTER_PASSW=conf["auth"]["admin_password"]

app = flask.Blueprint("admin_webserver", __name__, url_prefix="/admin")



@app.route("/reload")
def reload():

    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501

    starttime=time.time()
    um.force_reload()
    dm.force_reload()
    om.force_reload()
    return "fecthed data from database, took "+str(round(time.time()-starttime,5))+" seconds"

@app.route("/delete_session/<session_id>")
def delete_session(session_id):
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    se=sm.get(session_id)
    if se:
        sm.remove(se)
        return "session deleted"
    else:
        return "session not found", 404
    
@app.route("/get_orders")
def get_orders():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    orders=[]
    orders_d=om.loaded_orders
    for order in orders_d:
        order=om.get(order)
        orders.append(f"{order.id} | user : {um.get(order.user_id).email} | st : {order.status} | deliman : {order.deliveryman.email if order.deliveryman else "none"} | rest : {order.restaurant}")
    return flask.jsonify(orders), 221

@app.route("/fufill_order/<order_id>")
def fufill_order(order_id):
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    order=om.get(order_id)
    if order:
        order.fulfill()
        return "order fufilled"
    else:
        return "order not found", 404

@app.route("/get_order")
def get_order():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    idd=flask.request.args.get("id")
    order=om.get(idd)
    if order:
        return flask.jsonify([f'id : {order.id}',f'user : {um.get(order.user_id).email}',f'status : {order.status}',f'location : {order.location}',f'restaurent : {order.restaurant}',f'delivery_man : {order.deliveryman.email if order.deliveryman else "none"}',f'price : {order.price}']),223

@app.route("/set_order")
def set_order():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    idd=flask.request.args.get("id")
    key=flask.request.args.get("key")
    value=flask.request.args.get("to")
    order=om.get(idd)
    if order and key:
        if key == "Unload":
            order.unload()
        elif key == "Delete":
            order.delete()
        elif key=="Fulfill":
            order.fulfill()
        else:
            if key=='id':
                order.id=value
            if key=='user':
                order.user_id=um.getbyemail(value).id
            if key=='status':
                order.status=value
            if key=='restaurant':
                order.restaurant =value
            if key=='delivery_man':
                order.deliveryman = dm.getbyemail(value)
            if key=='price':
                order.price = value

            order.save()

    return "ok"

@app.route('/load_all_orders')
def load_all_orders():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    result=om.load_all()
    return f"done" if result else 'not found one',200
    
@app.route('/reload_orders')
def reload_orders():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    om.force_reload()
    return "done"


@app.route("/make_order",methods=["POST"])
def make_order():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    data=flask.request.json

    om.make_oreder(um.getbyemail(data["user_email"]).id,json.loads(data["order_items"]),data["restaurant"],json.loads(data["location"]),data["price"])

    return "ok"











    
@app.route("/get_dems")
def get_dems():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    dems=[]
    dems_d=dm.logged_in_users
    for dem in dems_d:
        dem=dm.get(dem)
        dems.append(f"{dem.id} | email : {dem.email} | online : {dem.online} | inprogress_order : {dem.inprogress_order} | destination : {essentials.get_place_by_coordinates(dem.destination["lat"],dem.destination["long"])}")
    return flask.jsonify(dems), 221

@app.route("/online_dems/<dem_id>")
def fufill_dem(dem_id):
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    dem=IMP.get(dem_id)
    if dem:
        dem.fulfill()
        return "dem fufilled"
    else:
        return "dem not found", 404

@app.route("/get_dem")
def get_dem():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    idd=flask.request.args.get("id")
    dem=dm.get(int(idd))
    if dem:
        response_data = flask.jsonify([f'id : {dem.id}', f'name : {dem.name}', f'email : {dem.email}', f'password : {dem.passw}', f'vehicle : {dem.vehicle}', f'online : {dem.online}', f'inprogress_order : {dem.inprogress_order}', f'destination : {dem.destination}', f'position : {dem.position}', f'token : {dem.token}', f'profilepicture : {dem.profilepicture}', f'createdat : {dem.createdat}', f'data : {dem.data}']), 223
        return response_data
    return "not found"

@app.route("/set_dems")
def set_dem():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    idd=flask.request.args.get("id")
    key=flask.request.args.get("key")
    value=flask.request.args.get("to")
    dem=dm.get(int(idd))
    if dem and key:
        if key == "Unload":
            dem.unload()
        elif key == "Delete":
            dem.delete()
        elif key=="Online":
            dem.online=True
        else:
            if key == 'name': dem.name = value
            if key == 'passw': dem.passw = value
            if key == 'email': dem.email = value
            if key == 'vehicle': dem.vehicle = value
            if key == 'online': dem.online = False
            if key == 'inprogress_order': dem.inprogress_order = value
            if key == 'destination': dem.destination = {"lat": 0, "long": 0} if value == "" else json.loads(value)
            if key == 'position': dem.position = json.loads(value)
            if key == 'id': dem.id = random.randint(10000, 99999) if value == "" else int(value)
            if key == 'token': dem.token = value
            if key == 'profilepicture': dem.profilepicture = value
            if key == 'createdat': dem.createdat = time.time() if value == "" else int(value)
            if key == 'data': dem.data = {} if value == "" else json.loads(value)


            dem.save()

    return "ok"

@app.route('/load_all_dems')
def load_all_dems():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    result=dm.load_all()
    return f"done" if result else 'not found one',200
    
@app.route('/reload_dems')
def reload_dems():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    IMP.force_reload()
    return "done"


@app.route("/make_dem",methods=["POST"])
def make_dem():
    token=flask.request.args.get("t")
    if token!=MESTER_PASSW:
        return "not implamented yet", 501
    data=flask.request.json

    IMP.make_oreder(um.getbyemail(data["user_email"]).id,json.loads(data["dem_items"]),data["restaurant"],json.loads(data["location"]),data["price"])

    return "ok"