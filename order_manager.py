import random
import database as database
import time
import json

from essentials import chose_best_delivery_man, reverse_geocode

loaded_orders = {}

import delivery_manager as dm

class Order:
    def __init__(self, user_id, order_items, restaurant, location, price, status="ordered", id="", createdat="", deliveryman="", deliveryman_id=""):
        self.user_id = user_id
        self.order_items = order_items
        self.id = random.randint(10000000000000,99999999999999) if id=="" else int(id)
        self.createdat = time.time() if createdat=="" else int(createdat)
        self.restaurant = restaurant
        self.location = location
        self.price = price
        self.status = status
        self.deliveryman = dm.get(deliveryman_id) if deliveryman_id != "" else deliveryman


    def fulfill(self):
        selected_deliveryman = chose_best_delivery_man(dm.logged_in_users.values(), self.location["location"])
        if selected_deliveryman:
            self.deliveryman = selected_deliveryman
            self.status = "picked up"
            self.deliveryman.inprogress_order = self.id
            self.deliveryman.destination = {"lat":reverse_geocode(self.location["location"])[0],"long":reverse_geocode(self.location["location"])[1]}
            self.save()
            self.deliveryman.save()
            return True
        return False


    def json(self):
        #returns json of the values in human readable format!
        return {
            "user_id": self.user_id,
            "order_items": self.order_items,
            "id": self.id,
            "createdat": self.createdat,
            "restaurant": self.restaurant,
            "location": self.location,
            "price": self.price,
            "status": self.status,
            "deliveryman": self.deliveryman.email if self.deliveryman != "" and self.deliveryman != False else ""
        }
    
    def save(self):
        database.set_row(table="orders",col="id",search=self.id,user=self.user_id,basket=json.dumps(self.order_items),restaurant=self.restaurant,location=json.dumps(self.location),price=self.price,status=self.status,createdat=round(self.createdat),deliveryman_id=self.deliveryman.id if self.deliveryman != "" and self.deliveryman != False else 0)

    def unload(self):
        self.save()
        del loaded_orders[self.id]

    def delete(self):
        del loaded_orders[self.id]
        database.delete_row(table="orders",col="id",search=self.id)


def get(id):
    try:
        id = int(id)
    except:
        return False
    if id in loaded_orders:
        return loaded_orders[id]
    read_order = database.read_database(table="orders", col="id", search=id)
    if len(read_order) == 0:
        return False
    read_order = read_order[0]
    loaded_orders[id] = Order(read_order[1], json.loads(read_order[2]), read_order[3], json.loads(read_order[4]), read_order[5], read_order[6], read_order[0], read_order[7], "", read_order[8] if read_order[8] != 0 else "")
    return loaded_orders[id]

def make_oreder(user_id, order_items, restaurant, location, price):
    order = Order(user_id, order_items, restaurant, location, price)
    database.write_database(table="orders", user=user_id, basket=json.dumps(order_items), restaurant=restaurant, location=json.dumps(location), price=price, status="ordered", id=order.id, createdat=round(order.createdat), deliveryman_id=order.deliveryman.id if order.deliveryman != "" and order.deliveryman != False else 0)
    loaded_orders[order.id] = order
    return order

def get_orders(user_id):
    orders = []
    for order in loaded_orders.values():
        if order.user_id == user_id:
            orders.append(order)
    read_orders = database.read_database(table="orders", col="user", search=user_id)
    for order in read_orders:
        if order[0] not in loaded_orders:
            loaded_orders[order[0]] = Order(order[1], json.loads(order[2]), order[3], json.loads(order[4]), order[5], order[6], order[0], order[7], "", order[8] if order[8] != 0 else "")
            orders.append(loaded_orders[order[0]])
    return orders



def force_reload():
    global loaded_orders
    liui = loaded_orders.keys()
    loaded_orders = {}
    for idd in liui:
        order=load_order(id=idd)
        if order:
            loaded_orders[idd]=order





def load_order(**args):
    read_order = database.read_database(table="orders", col=list(args.keys())[0], search=list(args.values())[0])
    if read_order:
        if len(read_order)>0:
            read_order = read_order[0]
            loaded_orders[read_order[0]] = Order(read_order[1], json.loads(read_order[2]), read_order[3], json.loads(read_order[4]), read_order[5], read_order[6], read_order[0], read_order[7], "", read_order[8] if read_order[8] != 0 else "")
            
    return False


#DONT USE IN PRODuction DANGEROUS
def load_all():
    global loaded_orders
    dw=database.read_database('orders')
    if not dw:
        return False
    for read_order in dw:
        loaded_orders[read_order[0]] = Order(read_order[1], json.loads(read_order[2]), read_order[3], json.loads(read_order[4]), read_order[5], read_order[6], read_order[0], read_order[7], "", read_order[8] if read_order[8] != 0 else "")
    return True

