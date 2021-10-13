from flask import Flask, request, send_file, jsonify, send_from_directory, render_template, flash, redirect, url_for
from passlib.hash import md5_crypt
from forms import MyForm, LoginForm, TestimonyForm 
from models import Products, Store, UserProducts, User, EmailSubcribers, Testimonial, app, db, LoginManager, login_required, login_user, logout_user, current_user, Transaction_Table, current_user
from is_safe_url import is_safe_url
from schema import user_schema
from flask_humanize import Humanize
from datetime import datetime
from pypaystack import Transaction
from mailing_server import mail_folks
import boto3, botocore, time, hashlib, hmac, json, os, shutil, request_func, mailing_server, basic_auth, string, random
import json, re

# from werkz/eug import secure_filename
from utils import upload_image, send_mail
from helper import generate_recommendation
from settings import PAYSTACK_SECRET

humanize = Humanize(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "please login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/callback", methods=["POST", "GET"])
def paycallback():
    print(request.method)

    if request.method == "POST":
        # print(data)
        data = request.json
        event = data.get("event")
        if event == "charge.success" and request.headers.get("X-Forwarded-For") in ['52.31.139.75', '52.49.173.169', '52.214.14.220']:
            reference = data["data"].get("reference")
            amount = data["data"].get('amount')
            email = data["data"].get('customer').get('email')
            cus_code = data["data"].get('customer').get('customer_code')
            paid_at = data["data"].get('paidAt')
            auth_code = data["data"].get('authorization').get('authorization_code')
            paid_time = datetime.now()
            get_transaction = Transaction_Table.query.filter_by(ref_no=reference).first()
            get_transaction.amount = amount
            get_transaction.auth_code = auth_code
            get_transaction.cus_code =  cus_code
            get_transaction.email = email
            get_transaction.paid_at = paid_time
            # Update User Table to reflect the payment made
            update_user = User.query.filter_by(email=email).first()

            data = get_transaction.product_data
            
            load_data = json.loads(data)
            
            for i in load_data:
                user_product = UserProducts(user_id=update_user.id, product_id=i.get("id"))
                db.session.add(user_product)

            # email=user_email, 
            # update_user.bet_49ja.is_paid_bot = True
            # update_user.bet_49ja.bot_type = "paid"
            # update_user.bet_49ja.has_compiled = False
            # update_user.bet_49ja.is_demo = False
            # Commit the changes

            # Transaction completed
            get_transaction.transaction_complete = True
            db.session.commit()
    else:
        return redirect(url_for('redirectThanks'))
    # else:
    #     return redirect("/my-downloads")


@app.route("/paystack", methods=["GET", "POST"])
def main():

    """
    All Response objects are a tuple containing status_code, status, message and data
    """
    # print(current_user)
    if not current_user:
        return redirect(url_for('login'))

    # print(dir(request))
    email = current_user.email
    
    # print(request.args)
    data = request.args.get("data")
    load_data = json.loads(data)
    
    bot_price = 0 
    for i in load_data:
        bot_price += int(i.get("price"))

    # turn to naira from kobo
    bot_price *= 100
    # bot_price = 25000 * 100
    #Instantiate the transaction object to handle transactions.  
    #Pass in your authorization key - if not set as environment variable PAYSTACK_AUTHORIZATION_KEY
    # email = "dataslid@gmail.com" "sk_test_faadf90960bad25e6a2b5c9be940792f928b73ac"
    transaction = Transaction(authorization_key=PAYSTACK_SECRET)
    # transaction_table = Transaction_Table.query.filter_by(email=email).first()
    
    # only Start another transaction when one is completed
    # if transaction_table:
    #     if transaction_table.transaction_complete:
    #         response = transaction.charge(email, f"{transaction_table.auth_code}", int(transaction_table.amount)) #+rge a customer N100.
    #         reference = response[3].get('reference')
    #         transaction = Transaction_Table(ref_no=reference)
    #         db.session.add(transaction)
    #         db.session.commit()
    #         return redirect('/my-downloads')
    #     else:
    init_transaction = transaction.initialize(email, bot_price)
    reference = init_transaction[3].get('reference')
    transaction = Transaction_Table(ref_no=reference, product_data=data)
    db.session.add(transaction)
    db.session.commit()
    return redirect(init_transaction[3].get('authorization_url'))    



@app.route("/search", methods=["GET"])
def search_market():
    search = request.args.get("search")
    if not search:
        search = None

    products = Products.query.filter(Products.title.op('regexp')(r'%s' %search)).all()
    # products = Products.query.all()[:8]
    return render_template("search.html", products=products)

def youtube_filter(youtube_link):
        youtube_pattern = re.match("^.*(youtu.be\/|v\/|embed\/|watch\?|youtube.com\/user\/[^#]*#([^\/]*?\/)*)\??v?=?([^#\&\?]*).*", youtube_link)
        if(youtube_pattern):
            youtube_id = youtube_pattern.group(3) 
            youtube_link = f'https://www.youtube.com/embed/{youtube_id}'  
        
        return youtube_link

@app.route("/add-items", methods=["GET", "POST"])
@login_required
def add_items():
    if request.method ==  "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("new_price")
        old_price = request.form.get("old_price")
        youtube_link = request.form.get("youtube_link")
        course_link = request.form.get("course_link")
        course_preview_link = request.form.get("course_preview_link")

        product_type = request.form.get("product_type")

        youtube_link = youtube_filter(youtube_link)
        course_link = youtube_filter(course_link)
        course_preview_link = youtube_filter(course_preview_link)
        store_id = current_user.store[0].id
        product = Products(title=title, store_id=store_id, product_type=product_type, course_link=course_link, course_preview_link=course_preview_link, description=description, youtube_link=youtube_link, price=price, old_price=old_price)
        db.session.add(product)
        
        
        for i in request.files:
            file_exists = request.files.get(i)

            if file_exists:
                if i == "product":
                    upload_image(product, file_exists, "download")
                elif i == "demo_product":
                    upload_image(product, file_exists, "demo")
                else:
                    upload_image(product, file_exists, "image")
    
        db.session.commit()
                    # product_id = product.id
                    # first = 0
                    # filename = file_exists.filename
                    # storage_key = os.environ.get("aws_key")
                    # storage_secret = os.environ.get("aws_secret")
                    # storage_bucket = "dataslid"
                    # urlExpiryTime = 604799
                    # download_expiry_time = time.time() + urlExpiryTime
                    # # Set Expiry time
                    # product.s3_expiry_time = download_expiry_time

                    # conn = boto3.client(
                    #     's3',
                    #     aws_access_key_id=storage_key,
                    #     aws_secret_access_key=storage_secret
                    #     )

                    # Key = f'images/{filename}'
                    # conn.upload_fileobj(file_exists, storage_bucket, Key)
                    # image_url = conn.generate_presigned_url(ClientMethod='get_object', Params={
                    #     'Bucket': storage_bucket,
                    #     'Key': Key
                    # }, ExpiresIn=urlExpiryTime)

                    
                    # product_image = ProductImage(image_url=image_url, product_id=product_id)
                    # db.session.add(product_image)
                    
                    # if first == 0:
                    #     product.thumbnail = image_url
                    #     product.thumbnail_key = Key
                
                    # db.session.commit()

                    # first += 1
        
        flash("You have successfully added new stuff for sell")
    users = User.query.all()
    return render_template("add_items.html", users=users)
    


# Redirect / to home
@app.route("/", methods=["GET"])
def no_route():
    return redirect(url_for("home"))
    
@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("dataslid/index.html")

@app.route("/marketplace", methods=["GET"])
def marketplace():
    products = Products.query.all()[:8]
    return render_template("home.html", products=products)

@app.route("/redirect", methods=["GET", "POST"])
def redirectThanks():
    return render_template("redirect.html")

@app.route("/market", methods=["GET"])
def market():
    products = Products.query.order_by(Products.datetime.desc()).all()
    # Inbox.query.filter_by(seen=False, user_id=current_user.id).order_by(Inbox.datetime.desc()).all()
    return render_template("market.html", products=products)

@app.route("/carts", methods=["GET"])
def carts():
    if current_user.is_authenticated:
        return render_template("carts.html")
    else:
        return redirect("/login?next=carts")

@app.route("/product/<int:pk>", methods=["GET"])
def product(pk):
    product = Products.query.filter_by(id=pk).first()
    recommended_hamlet = generate_recommendation(product.title)
    search = f'({recommended_hamlet.replace(" ", ")|(")})'
    all_products = Products.query.filter(Products.id != pk, Products.title.op('regexp')(r'%s' %search)).all()[:4]
    
    if not all_products:
        all_products = Products.query.all()[:4]
            
    if current_user.is_authenticated:

        user_purchased = UserProducts.query.filter_by(user_id=current_user.id, product_id =pk).first()
        return render_template("product.html", product=product, products=all_products, user_purchased=user_purchased)
    else:
        return render_template("product.html", product=product, products=all_products, user_purchased=None)


@app.route("/edit-item/<int:pk>", methods=["GET", "POST"])
def edit_item(pk):
    product = Products.query.filter_by(id=pk).first()
    if request.method == "POST":        
        if current_user.id != product.store.user.id:        
            flash("You are not allowed to edit this post!")
            users = User.query.all()
            return render_template("edit_item.html", users=users, product=product)
        
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("new_price")
        old_price = request.form.get("old_price")
        youtube_link = request.form.get("youtube_link")
        youtube_link = youtube_filter(youtube_link)

        store_id = current_user.store[0].id
        
        product.title = title
        product.store_id = store_id
        product.description = description
        product.youtube_link = youtube_link
        if price:
            product.price = price
        else:
            product.price = 0

        if old_price:
            product.old_price = old_price
        else:
            product.old_price = 0

        
        # product_id = product.id
        
        # first = 0
        for i in request.files:
            file_exists = request.files.get(i)

            if file_exists:
                if i == "product":
                    upload_image(product, file_exists, "download")
                elif i == "demo_product":
                    upload_image(product, file_exists, "demo")
                else:
                    upload_image(product, file_exists, "image")
        
        # db.session.add(product)
        db.session.commit()

        flash("You have successfully updated the product's details")
        return redirect(url_for('product', pk=product.id))

    users = User.query.all()
    return render_template("edit_item.html", users=users, product=product)
    
    

@app.route("/my-downloads", methods=["GET"])
def my_downloads():
    if current_user.is_authenticated:
        my_downloads = UserProducts.query.filter_by(user_id=current_user.id)
        # all_products = Products.query.all()[:8]
        return render_template("my_downloads.html", my_downloads=my_downloads)
    else:
        return redirect('/login?next=/my-downloads')

@app.route("/search-admin", methods=["GET"])
@login_required
def search():
    name = request.args.get("q")
    users = User.query.filter(User.username.like(f"%{name}%")).all()
    users_list = user_schema.dump(users)
    return {"users": users_list}

@app.route("/my-admin", methods=["GET"])
@login_required
def admin():
    users = User.query.all()
    email_subs = EmailSubcribers.query.all()
    email_len = len(email_subs)
    return render_template("admin.html", users=users, email_len=email_len, email_subs=email_subs)
    

@app.route("/manage-user", methods=["GET", "POST"])
@login_required
def manage_user():
    id =  request.args.get("id")
    user = User.query.get(id)
    if request.method == "POST":
        # print(request.form)
        update_pay = request.form.get("pay")
        update_admin = request.form.get("admin")
        update_building = request.form.get("building")
        user.is_admin = bool(update_admin)
        user.bet_49ja.is_building = bool(update_building)
        user.bet_49ja.is_paid_bot = bool(update_pay)
        if bool(update_pay):
            user.bet_49ja.bot_type = "paid"
        else:
            user.bet_49ja.bot_type = "demo"
            
        db.session.commit()
        # Get files from Admin
        botapp = request.files.get('botapp')
        # print(botapp)
        if botapp:
            filename = botapp.filename
            file_ext = filename.split('.')[1]
            if file_ext == "exe":
                storage_key = os.environ.get("aws_key")
                storage_secret = os.environ.get("aws_secret")
                storage_bucket = "betbots"
                conn = boto3.client(
                    's3',
                    aws_access_key_id=storage_key,
                    aws_secret_access_key=storage_secret
                    )

                key = f'user_bots/{filename}'
                conn.upload_fileobj(botapp, storage_bucket, key)
                user.bet_49ja.is_building = False
                user.bet_49ja.has_compiled = True
                user.bet_49ja.bot_path = key
                db.session.commit()

                flash(f"You have successfully update {user.username}'s ability and has uploaded files to S3")
            else:
                flash(f"The file uploaded must be an exe")

        flash(f"You have successfully update {user.username}'s ability")
        return redirect(f"/manage-user?id={user.id}")

    return render_template("manage_user.html", user=user)

@app.route("/testimony", methods=["GET", "POST"])
def testimony():
    form = TestimonyForm()
    testimonies = Testimonial.query.order_by(Testimonial.datetime.desc()).all()[:5]

    if request.method == "POST" and form.validate_on_submit():
        text = form.testimony.data
        testimony = Testimonial(testimony=text, user_id=current_user.id, datetime=datetime.now())
        db.session.add(testimony)
        db.session.commit()
        flash(f"Thanks {current_user.username}, for dropping your testimony") 
        return redirect(url_for("testimony"))
    
    return render_template("testimony.html", form=form, testimonies=testimonies)


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('my_downloads'))
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and md5_crypt.verify(password, user.password):
            login_user(user)
            next_page = request.args.get("next")
            is_safe_url(next_page, request.url)
            if is_safe_url(next_page, request.url):
                return redirect(next_page)
            return redirect("/market") 
        else:
            flash("e-mail or password is incorrect")
            return redirect("/login")
    else:
        return render_template("login.html", form=form)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('market'))
    
    form = MyForm()
    if request.method == "POST" and form.validate_on_submit():
        password = form.password.data
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        password = md5_crypt.hash(password)
        check_for_first_user = len(User.query.all())
        if not check_for_first_user:
            user = User(username=name, is_admin=True, email=email, phone=phone, password=password)
        else:
            user = User(username=name, is_admin=False, email=email, phone=phone, password=password)

        
        db.session.add(user)
        db.session.commit()
        
        # Initialize the store table
        store = Store(user_id=user.id)
        db.session.add(store)
        db.session.commit()
      
        flash("You have signed up successfully")    
        return redirect('/login')
    else:
        return render_template("sign_up.html", form=form)

@app.route("/subscribe-to-mail", methods=["GET", "POST"])
def email_subscribers():
    email = request.json.get("email")
    email_exists = EmailSubcribers.query.filter_by(email=email).first()
    total_emails = len(email_exists)
    
    if not email_exists:
        email_subscribers = EmailSubcribers(email=email)
        db.session.add(email_subscribers)
        db.session.commit()
    
    send_mail("Someone joined the newsletters", f"{email} just joined us at Dataslid tech, Total number = {total_emails}", "azeezolabode010@gmail.com")
    return dict(msg="success", ok=True)



@app.route("/logout")
def logout():
    logout_user()
    flash("You've logged out successfully, do visit soon")
    return redirect(url_for("login"))

@app.route("/admin-settings")
def admin_settings():
    email = EmailSubcribers.query.all()
    users = User.query.all()
    no_users = len(users)
    no_emails = len(email)
    
    return render_template("admin_settings.html", email=email, users=users, no_users=no_users, no_emails=no_emails)

if __name__  == '__main__':
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port="5000")