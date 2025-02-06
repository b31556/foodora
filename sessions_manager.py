import random
import json
import yaml
import time
import user_manager  as um

save_file="activesessions.json"


with open("config/configuration.yml","r") as f:
    conf = yaml.load(f,yaml.BaseLoader)

SESSION_IDLE_TIMEOUT=eval(conf["session_config"]["session_idle_timeout"])
MAX_TIMEOUT=eval(conf["session_config"]["max_timeout"])

sessions=[]

def generateSessionToken():
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(32))

class Session:
    def __init__(self, user, token="", id = "", createdat="", lastaction="",data=""):
        self.user=user
        self.createdat = time.time() if createdat=="" else createdat
        self.lastaction = time.time() if lastaction=="" else lastaction
        self.token = generateSessionToken() if token == "" else token
        self.id = random.randint(10000000000000,99999999999999) if id == "" else id

    def is_valid(self):
        if time.time() - self.lastaction > SESSION_IDLE_TIMEOUT:
            sessions.remove(self)
            return False
        if time.time() - self.createdat > MAX_TIMEOUT:
            sessions.remove(self)
            return False
        return True

    def use(self):
        self.lastaction = time.time()


def get(sessionid):
    """returns the Session object by the session id NOT THE TOKEN!"""
    for session in sessions:
        if str(session.id) == str(sessionid) and session.is_valid():
            session.use()
            return session
    return False
        
def getbytoken(token: str):
    """returns the Session object by a session token"""
    for session in sessions:
        if session.token == token and session.is_valid():
            session.use()
            return session
    return False

def remove(session: Session):
    """removes a session, closes it"""
    global sessions
    sessions.remove(session)
        
def make(user: um.User):
    """makes a new session for the user"""
    global sessions
    if isinstance(user,um.User):
        ses=Session(user)
        sessions.append(ses)
        return ses
    else:
        ses= Session(um.get(id))    
        sessions.append(ses)
        return ses



