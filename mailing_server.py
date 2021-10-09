from models import EmailSubcribers, app, User
from flask import request, render_template, jsonify
from utils import push_email
from os import environ

@app.route("/mail-users", methods=["POST"])
def mail_user():
    # sender_email = environ.get("email")
    recipient = request.json.get("user")
    message = request.json.get("mail")
    subject = request.json.get("subject")

    try:
        if recipient == "all":
            all_users = User.query.all()
            for user in all_users:
                push_email(user.email, subject, message)
        
        elif recipient == "email_subscriber":
            all_subs = EmailSubcribers.query.all()
            for subs in all_subs:
                push_email(subs.email, subject, message)

        else:
            push_email(recipient, subject, message)
        
        return jsonify({"ok": "message has been successfully delivered", "success": "Don't mind the Error "})
    except Exception as exc:
        print(exc)
        return jsonify({"ok": "", "Failed": "Something went wrong, send us a mail to dataslid@gmail.com"})

@app.route("/customer-mail", methods=["POST"])
def customer_mail():
    email = environ.get("email")
    message = request.form.get("message")
    subject = request.form.get("subject")
    
    name = request.form.get("name")
    if name:
        message = f"{message} - {name}"
        
    try:
        push_email(email, subject, message)
        return jsonify({"ok": "true"})
    except Exception as exc:
        print(exc)
        return jsonify({"ok": ""})


def mail_folks(recipient, subject, message):
    try:
        push_email(recipient, subject, message)
        return {"ok": "true"}
    except Exception as exc:
        print(f"fail... {str(exc)}")
        return {"ok": "", "msg": str(exc)}