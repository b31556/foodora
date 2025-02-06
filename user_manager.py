import random
import database as database
import time
import json

logged_in_users={}


def generateLongLivedToken():
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(64))

class User:
    def __init__(self, name, passw, email, id="", profilepicture="", data="", token="", createdat=""):
        self.name = name
        self.passw = passw
        self.email = email
        self.id = random.randint(10000000000000,99999999999999) if id=="" else int(id)
        self.token = generateLongLivedToken() if token=="" else token
        self.profilepicture = profilepicture
        self.createdat = time.time() if createdat=="" else int(createdat)
        self.data = {} if data=="" else data

    def auth(self,passw):
        return self.passw==passw
    
    def delete(self):
        database.delete_row(table="auth",col="id",search=self.id)

    def save(self):
        database.set_row(table="auth",col="id",search=self.id,name=self.name,email=self.email,pfp=self.profilepicture,id=self.id,passw=self.passw,createdat=round(self.createdat),data=json.dumps(self.data),token=self.token)


def make(name,passw, email, profilepic=""):
    user = User(name, passw, email, profilepicture=profilepic)
    logged_in_users[user.id]=user
    database.write_database(table="auth",name=name,email=email,pfp=profilepic,id=user.id,passw=passw,createdat=round(user.createdat),data=json.dumps({}),token=user.token)
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
        logged_in_users[id]=user
        return user
    return False

def getbytoken(token):
    for user in logged_in_users.values():
        if user.token==token:
            return user
    user=load_user(token=token)
    if user:
        logged_in_users[id]=user
        return user
    return False

def unload_user(id):
    if id in logged_in_users:
        del logged_in_users[id]


def save_all():
    for urs in logged_in_users:
        urs.save()
    

def force_reload():
    global logged_in_users
    liui=logged_in_users.keys()
    logged_in_users={}

    for idd in liui:
        user=load_user(id=idd)
        if user:
            logged_in_users[idd]=user

    






def load_user(**args):
    dat=database.read_database("auth",list(args.keys())[0],list(args.values())[0])
    if dat:
        if len(dat)>0:
            return User(dat[0][1],dat[0][3],dat[0][2],dat[0][0],dat[0][6],json.loads(dat[0][7]),dat[0][5],dat[0][4])
    False

