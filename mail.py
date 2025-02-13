import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml
import time
sentto={}

with open("config/configuration.yml","r") as f:
    conf = yaml.load(f,yaml.BaseLoader)

password = conf["auth"]["email_secret"]
sender_email = conf["auth"]["sender_email"]




def send_mail(emailaddress,template="",subject="",body="",**args):
    # Email credentials
    receiver_email = emailaddress

    if emailaddress in sentto:
        if time.time()-sentto[emailaddress] > 30:
            pass
        else:
            return False
        
    if template!="":
        with open(f"config/email_template/{template}.txt","r") as f:
            subject=f.readlines()[0]
            body = ""
            for line in f.readlines()[2:]:
                body+=line


    # Create the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email

    msg["Subject"] = subject

    # Email body
    body = body.replace("{link}",args["link"])
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)  # Login
            server.sendmail(sender_email, receiver_email, msg.as_string())  # Send
        print("Email sent successfully!")
        sentto[emailaddress]=time.time()
        return True
    except Exception as e:
        print("Error:", e)
        return False
