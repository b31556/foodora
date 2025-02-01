import random
import database as database
import time
import json

logged_in_users={}


def generateLongLivedToken():
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(64))


class User:
    def __init__(self, name, passw, email, vehicle, position: dict["lat": int,"long": int], destination="", inprogress_order = "", id="", profilepicture="", data="", token="", createdat=""):
        self.name = name
        self.passw = passw
        self.email = email
        self.vehicle = vehicle
        self.online = False
        self.inprogress_order = inprogress_order
        self.destination = {"lat":0,"long":0} if destination=="" else destination
        self.position = position
        self.id = random.randint(10000,99999) if id=="" else int(id)
        self.token = generateLongLivedToken() if token=="" else token
        self.profilepicture = profilepicture
        self.createdat = time.time() if createdat=="" else int(createdat)
        self.data = {} if data=="" else data

    def auth(self,passw):
        return self.passw==passw
    
    def save(self):
        database.set_row(table="delivery_mans",col="id",search=self.id,name=self.name,email=self.email,pfp=self.profilepicture,id=self.id,passw=self.passw,createdat=round(self.createdat),data=json.dumps(self.data),token=self.token,vehicle=self.vehicle,position=json.dumps(self.position),destination=json.dumps(self.destination),inprogress_order=self.inprogress_order)

def make(name,passw, email, vehicle, position: dict["lat": int,"long": int], profilepic=""):
    user = User(name, passw, email, profilepicture=profilepic, vehicle=vehicle, position=position)
    logged_in_users[user.id]=user
    database.write_database(table="delivery_mans",name=name,email=email,pfp=profilepic,id=user.id,passw=passw,createdat=round(user.createdat),data=json.dumps({}),token=user.token,vehicle=vehicle,position=json.dumps(position),destination=json.dumps({"lat":0,"long":0}),inprogress_order=user.inprogress_order)
    return user

def get(id):
    if id in logged_in_users:
        return logged_in_users[id]
    else:
        user=load_user(id=id)
        if user:
            logged_in_users[id]=user
            return user
    return False
    
def getbyemail(email):
    for user in logged_in_users.values():
        if user.email==email:
            return user
    user=load_user(email=email)
    if user:
        logged_in_users[user.id]=user
        return user
    return False

def getbytoken(token):
    for user in logged_in_users.values():
        if user.token==token:
            return user
    user=load_user(token=token)
    if user:
        logged_in_users[user.id]=user
        return user
    return False

def unload_user(id):
    if id in logged_in_users:
        del logged_in_users[id]


def save_all():
    for urs in logged_in_users:
        urs.save()
    

    





def load_user(**args):
    dat=database.read_database("delivery_mans",list(args.keys())[0],list(args.values())[0])
    if dat:
        if len(dat)>0:
            dat=dat[0]
            return User(dat[1],dat[4],dat[2],dat[8],json.loads(dat[9]),json.loads(dat[10]),json.loads(dat[11]),dat[0],dat[3],json.loads(dat[6]),dat[7],dat[5])
    
    False

