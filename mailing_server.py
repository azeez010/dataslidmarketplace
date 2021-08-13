from models import app, User
from flask import request, render_template, jsonify
from utils import push_email
from os import environ

@app.route("/mail-users", methods=["POST"])
def mail_user():
    sender_email = environ.get("email")
    recipient = request.json.get("user")
    message = request.json.get("mail")
    subject = request.json.get("subject")
    try:
        if recipient == "all":
            all_users = User.query.all()
            for user in all_users:
                push_email(user.email, subject, message)
                
        else:
            push_email(recipient, subject, message)
        
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