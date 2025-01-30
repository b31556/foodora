import random
import database as database
import time
import json

loaded_orders = {}


class Order:
    def __init__(self, user_id, order_items, restaurant, location, price, status="ordered", id="", createdat=""):
        self.user_id = user_id
        self.order_items = order_items
        self.id = random.randint(10000000000000,99999999999999) if id=="" else int(id)
        self.createdat = time.time() if createdat=="" else int(createdat)
        self.restaurant = restaurant
        self.location = location
        self.price = price
        self.status = status

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
            "status": self.status
        }





def make_oreder(user_id, order_items, restaurant, location, price):
    order = Order(user_id, order_items, restaurant, location, price)
    database.write_database(table="orders", user=user_id, basket=json.dumps(order_items), restaurant=restaurant, location=json.dumps(location), price=price, status="ordered", id=order.id, createdat=round(order.createdat))
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
            if order[6] == "ordered":
                loaded_orders[order[0]] = Order(order[1], json.loads(order[2]), order[3], json.loads(order[4]), order[5], order[6], order[0], order[7])
            orders.append(loaded_orders[order[0]])
    return orders