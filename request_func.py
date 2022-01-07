from models import User, Make_request, Testimonial, app, db, LoginManager, login_required, login_user, logout_user, current_user
from flask import Flask, request, jsonify, send_from_directory, render_template, flash, redirect, url_for
from forms import RequestForm
from schema import request_schema
from math import ceil
from mailing_server import mail_folks
from datetime import datetime
import os

@app.route("/request", methods=["GET", "POST"])
@login_required
def make_request():
    email = os.environ.get("email")
    user_email = current_user.email 
    username = current_user.username
    form = RequestForm()
    if request.method == "POST" and form.validate_on_submit():
        text = form.request.data
        make_request = Make_request(request=text, user_id=current_user.id, datetime=datetime.now())
        db.session.add(make_request)
        db.session.commit()
        subject = f"{username} Made a request from betbots site"
        message= f"{text} from {user_email}"
        mail_folks(email, subject, message)

        flash(f"{current_user.username}, Your request(s) has been submitted and are been tend to by our customer care") 
        return redirect(url_for("make_request"))
    return render_template("request.html", form=form)

@app.route("/new-requests", methods=["GET"])
@login_required
def new_request():
    post_per_page = 1
    page = request.args.get("page")
    if page:
        page = int(page)
        start_page = post_per_page * (page - 1)
        end_page = post_per_page * page
        new_requests = Make_request.query.order_by(Make_request.datetime.desc()).all()[start_page:end_page]
        request_list = request_schema.dumps(new_requests)
        return {"requests": request_list}
    else:
        new_requests = Make_request.query.order_by(Make_request.datetime.desc()).all()
        no_of_requests = len(new_requests) 
        max_pagination_no  = ceil(no_of_requests / post_per_page) 
        
        requests = new_requests[:post_per_page]
        return render_template("new_request.html", new_requests=requests, max_pagination_no=max_pagination_no)

@app.route("/seen-requests", methods=["GET"])
@login_required
def seen_request():
    requests = Make_request.query.filter_by(not_seen=True).all()
    for each_request in requests:
        each_request.not_seen = False

    db.session.commit()
    return "success"


