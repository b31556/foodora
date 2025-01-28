from flask import Blueprint, render_template, request, redirect, url_for, jsonify, send_file, make_response, render_template
from flask_limiter import Limiter, RateLimitExceeded
import requests
import random
import time
from database import read_database, write_database

import sessions_manager as sm
import user_manager as um

app = Blueprint('auth', __name__, url_prefix='/auth')

CLIENT_ID = '541304192962-2c2uqhq1i5c3p0g64qqcvssoakbibon1.apps.googleusercontent.com'   ## GOOGLE CLOUD CREDENTIALS
CLIENT_SECRET = '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'

def get_client_ip():
    forwarded_for = request.headers.get("X-Forwarded-For", None)
    if forwarded_for:
        # Ha több IP van, az első a kliens IP
        print(forwarded_for.split(",")[0].strip())
        return forwarded_for.split(",")[0].strip()
    print(request.remote_addr)
    return request.remote_addr


limiter=None

REDIRECT_URI = 'http://nationscity.eu:8945/auth/callback'



@app.route("/api/login")
def apilogin():
    email=request.args.get("email")
    password=request.args.get("pass")
    if email and password:
        user=um.getbyemail(email)
        if user:
            if user.passw==password:
                return jsonify({"code":200,"token":sm.make(user).token})
            else:
                return jsonify({"code":401,"message":"Invalid email or password"}), 401
        else:
            return jsonify({"code":401,"message":"Not existing user"}), 401
    else:
        return jsonify({"code":400,"message":"Missing email or password arg"}), 400
@app.route("/api/gettoken")
def gettoken():
    email=request.args.get("email")
    password=request.args.get("pass")
    if email and password:
        user=um.getbyemail(email)
        if user:
            if user.passw==password:
                return jsonify({"code":200,"token":user.token})
            else:
                return jsonify({"code":401,"message":"Invalid email or password"}), 401
        else:
            return jsonify({"code":401,"message":"Not existing user"}), 401
    else:
        return jsonify({"code":400,"message":"Missing email or password arg"}), 400
@app.route("/api/loginbytoken")
def loginbytokenapi():
    token=request.args.get("token")
    if token:
        user=um.getbytoken(token)
        if user:
            return jsonify({"code":200,"token":sm.make(user).token})
        else:
            return jsonify({"code":401,"message":"Invalid token"}), 401
    else:
        return jsonify({"code":400,"message":"Missing token arg"}), 400


@app.route('/loginbygoogle')
def loginbygoogle():
    """Redirect to Google's OAuth 2.0 authentication page."""
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=openid email profile"
    )
    return redirect(google_auth_url) 


@app.route("/confirm")
def info():
    token=request.cookies.get("sessiontoken")
    redirecturl=request.cookies.get("redirect")
    if token:
        ses=sm.getbytoken(token)
        if ses:
            if redirecturl:
                return redirect(redirecturl)
            return redirect("/")
    return jsonify({"message":"Invalid email or password","code":401}), 401


@app.route("/login")
def login():
    try:
        with limiter.limit("5/minute"):
            email = request.args.get('email')
            passw = request.args.get('pass')
            return handlelogin(email,passw)
    except RateLimitExceeded as e:
        return jsonify({"message": f"Too many requests! slow down; only {e.description} is allowed, (you can still use login by google)"}), 401




def handlelogin(email, passw="", name="", googlehandled=False, pfp=""):
    """
    Handle user login or registration.

    Parameters:
    email (str): The user's email address.
    passw (str): The user's password.
    name (str): The user's name.
    googlehandled (bool): Whether the login is handled by Google (skips password auth).
    pfp (str): The user's profile picture URL.

    Returns:
    Response: A Flask response object with the login result.
    """
    user = um.getbyemail(email)
    redirecturl = request.cookies.get("redirect")
    if user:
        return handle_existing_user(user, passw, googlehandled, redirecturl)
    else:
        return handle_new_user(email, passw, name, googlehandled, pfp, redirecturl)


def handle_existing_user(user, passw, googlehandled, redirecturl):
    if user.auth(passw) or googlehandled:
        session = sm.make(user)
        return jsonify({"code":200, "message":"Login Sucessful", "token":session.token})
    else:
        return jsonify({"code":202}), 202


def handle_new_user(email, passw, name, googlehandled, pfp, redirecturl):
    try:
        a, b = email.split("@")
        if a == "" or b == "":
            raise Exception
        if passw == "":
            raise Exception
    except:
        if not googlehandled:
            return jsonify({"code":202}), 202

    user = um.make(email.split("@")[0] if name == "" else name, passw, email, pfp)
    session = sm.make(user)
    returnn = jsonify({"code":201, "message":"Registered Sucessfully", "token":session.token})

    return create_response(session, googlehandled, redirecturl)


def create_response(session, googlehandled, redirecturl):
    resp = make_response(jsonify({"code":202}) if not googlehandled else (redirect("/") if not redirecturl else redirect(redirecturl)), 302 if googlehandled else 202)
    
    # Set a custom session cookie
    resp.set_cookie(
        key='sessiontoken',                # Cookie name
        value=session.token,               # Cookie value
        httponly=True,                     # Prevent JavaScript access
        secure=False, # Only send over HTTPS #! MAKE THIS TRUE FOR PRODUCTION!
        samesite='Lax'                     # Prevent CSRF attacks
    )
    if redirecturl:
        resp.delete_cookie(
            key='redirect'
        )
    return resp

@app.route("/loginbytoken")
def loginbt():
    longtoken = request.args.get('longlivedacesstoken')
    user=um.getbytoken(longtoken)
    if user:
        session=sm.make(user)
        return jsonify({"code":200,"message":"Login Sucessful","token":session.token})
    return jsonify({"code":401,"message":"invalid token"})

@app.route("/getlonglivedacesstoken")
def getl():
    with limiter.limit("5/minute"):
        email = request.args.get('email')
        passw = request.args.get('pass')

        user=um.getbyemail(email)
        if user:
            if user.passw == passw:
                return jsonify({"code":200,"message":"Token Sucessfully Generated","token":user.token}),596

    return jsonify({"code":401,"message":"invalid email or passw"})
    

@app.route("/logout")
def logout():
    tokenc=request.cookies.get("sessiontoken")
    token = request.args.get('token')
    if tokenc:
        token=tokenc
    session=sm.getbytoken(token)
    if not token:
        return jsonify({"code":401,"message":"Missing Token"}), 401
    if session:
        sm.remove(session)
        return redirect("/")
    else:
        return jsonify({"code":401,"message":"Invalid Token"}), 401


@app.route("/callback")
def callback():
    """Handle the OAuth callback from Google."""
    # Google sends a code in the 'code' parameter
    code = request.args.get('code')

    if not code:
        return "Error: No code received", 400

    # Exchange the code for an access token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }

    token_response = requests.post(token_url, data=data)
    token_data = token_response.json()

    if 'access_token' not in token_data:
        return "Error: No access token received", 400

    access_token = token_data['access_token']

    # Use the access token to fetch the user's info from Google
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {'Authorization': f'Bearer {access_token}'}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()

    # You can store the user information in the session or a database
    #session['user_info'] = user_info
    if user_info.get("email_verified",False) == True:
        return handlelogin(user_info.get("email"),googlehandled=True,pfp=user_info.get("picture"),name=user_info.get("name"))
    else:
        return "email not verifried"










def makeuser(email: str, passw: str, longliviedacesstoken: str = ""):
    write_database(email=email,passw=passw,token=longliviedacesstoken,createdat=time.time(),table="auth")