import boto3, os, json, re
import git
from flask import  request, render_template, flash, redirect, url_for
from passlib.hash import md5_crypt
from is_safe_url import is_safe_url
from flask_humanize import Humanize
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, current_user
from forms import MyForm, LoginForm, TestimonyForm 
from models import ProductAuth, Blog, Products, Store, UserProducts, User, EmailSubcribers, Testimonial, app, db, Transaction_Table
from schema import user_schema
from datetime import datetime
from pypaystack import Transaction, errors
from pypaystack import utils as pay_utils

from utils import upload_image, send_mail, get_two_random_number, create_product_key, validate_email
from helper import generate_recommendation
from settings import PAYSTACK_SECRET
# For import all file basic_auth at once
import import_all

humanize = Humanize(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "please login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class MyTransaction(Transaction):
    def initialize(
        self, email, amount, currency, plan=None, reference=None, channel=None, metadata=None
    ):
        """
        Initialize a transaction and returns the response
        args:
        email -- Customer's email address
        amount -- Amount to charge
        plan -- optional
        Reference -- optional
        channel -- channel type to use
        metadata -- a list if json data objects/dicts
        """
        amount = pay_utils.validate_amount(amount)

        if not email:
            raise errors.InvalidDataError("Customer's Email is required for initialization")

        url = self._url("/transaction/initialize")
        payload = {
            "email": email,
            "amount": amount,
            "currency": currency,
        }

        if plan:
            payload.update({"plan": plan})
        if channel:
            payload.update({"channels": channel})
        if reference:
            payload.update({"reference": reference})
        if metadata:
            payload = payload.update({"metadata": {"custom_fields": metadata}})

        return self._handle_request("POST", url, payload)
# user_location = GeoIP2()
# try:
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = request.META.get('REMOTE_ADDR')

#     user_city = user_location.city(ip)
#     save_location.city = user_city['city']
#     save_location.country = user_city["country_code"]
    


#Route for the GitHub webhook
@app.route('/git_update', methods=['POST'])
def git_update():
  repo = git.Repo('./market')
  origin = repo.remotes.origin
  repo.create_head('main', 
  origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
  origin.pull()
  return '', 200

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
            
            for _product_id in load_data:
                product_id = _product_id.get("id")
                # _user_product = UserProducts.query.filter_by(user_id=update_user.id, product_id=product_id).first()
                # if _user_product:
                user_product = UserProducts(user_id=update_user.id, product_id=product_id)
                db.session.add(user_product)
                # Create product key
                create_product_key(product_id)

            get_transaction.transaction_complete = True
            db.session.commit()
            # Delete failed transactions
            failed_transactions = Transaction_Table.query.filter_by(amount="")
            db.session.delete(failed_transactions)
            db.session.commit()
    else:
        return redirect(url_for('redirectThanks'))

# @app.route("/temp", methods=["GET", "POST"])
# def temp():
#     product_id = request.args.get('product_id')
#     _user_product = UserProducts.query.filter_by(user_id=current_user.id, product_id=product_id).first()
#     if _user_product:
#         user_product = UserProducts(user_id=current_user.id, product_id=product_id)
#         db.session.add(user_product)
#         # Create product key
#         create_product_key(product_id)
#         db.session.commit()
#     return redirect(url_for('my_downloads'))
            

@app.route("/paystack", methods=["GET", "POST"])
def paystack():

    """
    All Response objects are a tuple containing status_code, status, message and data
    """
    # print(current_user)
    if not current_user:
        return redirect(url_for('login'))

    if current_user.is_authenticated:
        email = current_user.email
    else:
        email = request.form.get('email')
    data = request.form.get("data")
    load_data = json.loads(data)
    print(load_data)
    
    bot_price = 0 
    for i in load_data:
        bot_price += int(i.get("price"))

    # turn to naira from kobo
    bot_price *= 100
    # metadata = {
    #     "currency": "NGN",
    #     "amount": bot_price
    # }
    # bot_price = 25000 * 100
    #Instantiate the transaction object to handle transactions.  
    #Pass in your authorization key - if not set as environment variable PAYSTACK_AUTHORIZATION_KEY
    # email = "dataslid@gmail.com" "sk_test_faadf90960bad25e6a2b5c9be940792f928b73ac"
    transaction = MyTransaction(authorization_key=PAYSTACK_SECRET)
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
    #  metadata=metadata NGN
    init_transaction = transaction.initialize(email, bot_price, "NGN")
    # print(init_transaction)
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
        description = request.form.get("ckeditor")
        price = request.form.get("new_price")
        old_price = request.form.get("old_price")
        youtube_link = request.form.get("youtube_link")
        course_link = request.form.get("course_link")
        support_link = request.form.get("support_link")
        affliate = request.form.get("affliate")
        affliate_commission = request.form.get("affliate_commission")

        accept_affliate = bool(affliate)
        
        course_preview_link = request.form.get("course_preview_link")

        product_type = request.form.get("product_type")

        youtube_link = youtube_filter(youtube_link)
        course_link = youtube_filter(course_link)
        course_preview_link = youtube_filter(course_preview_link)
        store_id = current_user.store[0].id
        product = Products(title=title, store_id=store_id, product_type=product_type, course_link=course_link, support_link=support_link, course_preview_link=course_preview_link, description=description, youtube_link=youtube_link, price=price, old_price=old_price, accept_affliate=accept_affliate, affliate_commission=affliate_commission)
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
    return redirect(url_for("marketplace"))
    
@app.route("/home", methods=["GET", "POST"])
def home():
    return redirect(url_for("marketplace"))


@app.route("/services", methods=["GET", "POST"])
def services():
    return render_template("dataslid/index.html")

@app.route("/marketplace", methods=["GET"])
def marketplace():
    ip_addr = request.remote_addr
    # loc = check_location(ip_addr)
    # print(loc)
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
    referral = request.args.get("ref")

    recommended_hamlet = generate_recommendation(product.title)
    search = f'({recommended_hamlet.replace(" ", ")|(")})'
    all_products = Products.query.filter(Products.id != pk, Products.title.op('regexp')(r'%s' %search)).all()[:4]
    
    if not all_products:
        products = Products.query.filter(Products.id != pk)
        products_len = products.count()
        start, end = get_two_random_number(products_len)
    
        # Slice Data out
        all_products = products.all()[start:end]
            
    if current_user.is_authenticated:
        user_purchased = UserProducts.query.filter_by(user_id=current_user.id, product_id =pk).first()
        return render_template("product.html", product=product, products=all_products, referral=referral, user_purchased=user_purchased,)
    else:
        return render_template("product.html", product=product, products=all_products, referral=referral, user_purchased=None)


@app.route("/edit-item/<int:pk>", methods=["GET", "POST"])
def edit_item(pk):
    product = Products.query.filter_by(id=pk).first()
    if request.method == "POST":        
        if current_user.id != product.store.user.id:        
            flash("You are not allowed to edit this post!")
            users = User.query.all()
            return render_template("edit_item.html", users=users, product=product)
        
        title = request.form.get("title")
        description = request.form.get("ckeditor")
        price = request.form.get("new_price")
        old_price = request.form.get("old_price")
        youtube_link = request.form.get("youtube_link")
        support_link = request.form.get("support_link")
        affliate = request.form.get("affliate")
        affliate_commission = request.form.get("affliate_commission")
        accept_affliate = bool(affliate)
        
        youtube_link = youtube_filter(youtube_link)
        
        store_id = current_user.store[0].id
        
        product.title = title
        product.support_link = support_link
        product.store_id = store_id
        product.description = description
        product.youtube_link = youtube_link
        product.affliate_commission = affliate_commission
        product.accept_affliate = accept_affliate
        product.youtube_link = youtube_link

        if price:
            product.price = price
        else:
            product.price = 0

        if old_price:
            product.old_price = old_price
        else:
            product.old_price = 0

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

        flash("You have successfully updated the product's details")
        return redirect(url_for('product', pk=product.id))

    users = User.query.all()
    return render_template("edit_item.html", users=users, product=product)
    
    

@app.route("/my-downloads", methods=["GET"])
def my_downloads():
    if current_user.is_authenticated:
        my_downloads = UserProducts.query.filter_by(user_id=current_user.id)
        return render_template("my_downloads.html", my_downloads=my_downloads)
    else:
        return redirect('/login?next=/my-downloads')

@app.route("/download", methods=["GET"])
def download():
    if current_user.is_authenticated:
        product_id = request.args.get("product_id")
        product = UserProducts.query.filter_by(product_id=product_id).first()
        product_key = ProductAuth.query.filter_by(product_id=product_id).first()
        return render_template("download.html", download=product, product_key=product_key)
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
    next_page = request.args.get("next")
       
    if current_user.is_authenticated:
        return redirect(url_for('market'))
    
    form = MyForm()
    if request.method == "POST" and form.validate_on_submit():
        next_page = request.args.get("next")
        
        password = form.password.data
        email = form.email.data
        password = md5_crypt.hash(password)
        check_for_first_user = len(User.query.all())
        user = User(email=email, password=password)
        
        if not check_for_first_user:
            user.is_admin = True
        
        db.session.add(user)
        db.session.commit()
        
        user = User.query.filter_by(email=email).first()
        login_user(user)
        is_safe_url(next_page, request.url)
        if is_safe_url(next_page, request.url):
            return redirect(next_page)
        return redirect("/market")

        # Initialize the store table
        # store = Store(user_id=user.id)
        # db.session.add(store)
        # db.session.commit()
      
        flash("You have signed up successfully")    
        return redirect('/login')
    else:
        return render_template("sign_up.html", form=form)

@app.route("/subscribe-to-mail", methods=["GET", "POST"])
def email_subscribers():
    email = request.json.get("email")
    is_valid = validate_email(email)
    if is_valid:
        email_exists = EmailSubcribers.query.filter_by(email=email).first()
    
        if not email_exists:
            email_subscribers = EmailSubcribers(email=email)
            db.session.add(email_subscribers)
            db.session.commit()
        
        send_mail("Thanks for joining our Newsletter", "We really appreciate you joining our news letter and we promise to bless your e-mail account with good contents.", email)
        send_mail("Someone joined the newsletters", f"{email} just joined us at Dataslid tech", "azeezolabode010@gmail.com")
        return dict(msg="success", ok=True)
    else:
        return dict(msg="Failed", ok="Failed")


@app.route("/unsubscribe-to-mail", methods=["GET", "POST"])
def email_unsubscribe():
    _email = request.args.get("email")
    email = EmailSubcribers.query.filter_by(email=_email).first()
    if email:
        db.session.delete(email)
        db.session.commit()
        flash("You have successful opt-out of our amazing newsletter")
    else:
        flash("Email doesn't exist")
    return redirect(url_for("login"))



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

@app.route("/sitemap")
@app.route("/sitemap/")
@app.route("/sitemap.xml")
def sitemap():
    """
        Route to dynamically generate a sitemap of your website/application.
        lastmod and priority tags omitted on static pages.
        lastmod included on dynamic content such as blog posts.
    """
    from flask import make_response, request, render_template
    import datetime
    from urllib.parse import urlparse

    host_components = urlparse(request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc

    # Static routes with static content
    static_urls = list()
    for rule in app.url_map.iter_rules():
        if not str(rule).startswith("/admin") and not str(rule).startswith("/user"):
            if "GET" in rule.methods and len(rule.arguments) == 0:
                url = {
                    "loc": f"{host_base}{str(rule)}"
                }
                static_urls.append(url)

    # Dynamic routes with dynamic content
    dynamic_urls = list()
    blog_posts = Blog.query.all()
    for post in blog_posts:
        url = {
            "loc": f"{host_base}/blog?id={post.id}&amp;title={post.title}",
            }
        dynamic_urls.append(url)

    xml_sitemap = render_template("sitemap.xml", static_urls=static_urls, dynamic_urls=dynamic_urls, host_base=host_base)
    response = make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"

    return response
    
if __name__  == '__main__':
    db.create_all()
    PORT = os.environ.get("PORT")
    
    if PORT:
        app.run(debug=False, port=PORT)
    else:
        app.run(debug=True, host="0.0.0.0", port="5000")