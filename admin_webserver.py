import flask
import time

import user_manager as um
import delivery_manager as dm
import order_manager as om

import sessions_manager as sm
import delivery_session_manager as dsm

MESTER_PASSW = "mester911"

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
        orders.append(f"{order.id} | {order.status} | {order.deliveryman.email} | {order.restaurant}")
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
        return flask.jsonify([f'id : {order.id}',f'user : {um.get(order.user_id).email}',order.status,order.location,order.restaurant,order.deliveryman.email,order.price]),223

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
            pass
        else:
            if key=='id':
                order.id=value
            if key=='user':
                order.user_id=um.getbyemail(value).id
            

            
