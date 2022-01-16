import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import UserMixin
from datetime import date, datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_ckeditor import CKEditor



app = Flask(__name__)

URL = os.environ.get("DATABASE_URL")

if URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://azeez:azeez007@localhost/dataslid'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://dataslid:azeez007@dataslid.mysql.pythonanywhere-services.com/dataslid$betbot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SECRET_KEY'] = "d27e0926-13d9-11eb-900d-18f46ae7891e"
app.config['TOKEN_EXPIRY_TIME'] = "10"
app.config['CKEDITOR_PKG_TYPE'] = 'full'

ckeditor = CKEditor(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class User(db.Model, UserMixin ):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_merchant = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(200))
    password = db.Column(db.String(150))
    merchant_wallet = db.Column(db.Integer, default=0)
    Referral_wallet = db.Column(db.Integer, default=0)
    account_number = db.Column(db.String(10))
    account_name = db.Column(db.String(100))
    account_bank = db.Column(db.String(40))


class Transaction_Table(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(50))
    amount = db.Column(db.String(15))
    # For recurring charges
    auth_code = db.Column(db.String(30))
    email = db.Column(db.String(30))
    cus_code = db.Column(db.String(30))
    paid_at = db.Column(db.String(80))
    product_data = db.Column(db.Text)
    transaction_complete = db.Column(db.Boolean, default=False)
    
class Make_request(db.Model):
    __tablename__ = "make_request"
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='make_request', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    request = db.Column(db.Text)
    not_seen = db.Column(db.Boolean, default=True)
    datetime = db.Column(db.DateTime, default=datetime.now())

class Testimonial(db.Model):
    __tablename__ = "testimonial"
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='testimonial', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    testimony = db.Column(db.Text)
    datetime = db.Column(db.DateTime, default=datetime.now())

class Reset_password(db.Model):
    __tablename__ = 'reset_password'
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='reset_password', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    mail = db.Column(db.String(100))
    dateTime = db.Column(db.String(500), default=0)
    token = db.Column(db.String(150))
    
class Confirm_mail(db.Model):
    __tablename__ = 'confirm_mail'
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100))
    user_details = db.Column(db.String(500))
    dateTime = db.Column(db.Integer)
    dateTime = db.Column(db.String(500), default=0)
    token = db.Column(db.String(150))

class Buy_pin(db.Model):
    __tablename__ = 'buy_pin'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(150))
    datetime = db.Column(db.DateTime, default=datetime.now())
    
class Subcribe_pin(db.Model):
    __tablename__ = 'subscribe_pin'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(150))
    datetime = db.Column(db.DateTime, default=datetime.now())
    

class Financial_data(db.Model):
    __tablename__ = 'financial_data'
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='financial_data', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    datetime = db.Column(db.DateTime, default=datetime.now())
    price = db.Column(db.String(15))
    bot_type = db.Column(db.String(60))


class Store(db.Model):
    __tablename__ = 'store'
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='store', lazy=True)
    store_name = db.Column(db.String(300))
    store_description = db.Column(db.Text)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    datetime = db.Column(db.DateTime, default=datetime.now())
    store_banner_url = db.Column(db.String(1000))
    store_logo_url = db.Column(db.String(1000))
    
class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    old_price = db.Column(db.Integer)
    accept_affliate = db.Column(db.Boolean, default=False)
    affliate_commission = db.Column(db.Integer, default=0)
    store  = db.relationship(Store, backref='products', lazy=True)
    store_id = db.Column(db.Integer(), db.ForeignKey(Store.id))
    datetime = db.Column(db.DateTime, default=datetime.now())
    
    has_product_key = db.Column(db.Boolean, default=False)
    
    support_link = db.Column(db.String(1500))
    # Links
    product_type = thumbnail = db.Column(db.String(100)) 
    course_preview_link = db.Column(db.String(1000))
    course_link = db.Column(db.String(1000))
    
    youtube_link = db.Column(db.String(1000))
    download_link = db.Column(db.String(3000))
    demo_link = db.Column(db.String(3000))
    thumbnail = db.Column(db.String(2000)) 
    
    # S3 Keys 
    demo_key = db.Column(db.String(1000))
    thumbnail_key = db.Column(db.String(1000)) 
    download_key = db.Column(db.String(1000)) 
    s3_expiry_time = db.Column(db.Integer)
    

class ProductImage(db.Model):
    __tablename__ = 'product_image'
    id = db.Column(db.Integer, primary_key=True)
    product = db.relationship(Products, backref='product_image', lazy=True)
    product_id = db.Column(db.Integer(), db.ForeignKey(Products.id))
    image_url = db.Column(db.String(1000))


class UserProducts(db.Model):
    __tablename__ = 'userproducts'
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='userproducts', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    product = db.relationship(Products, backref='userproducts', lazy=True)
    product_id = db.Column(db.Integer(), db.ForeignKey(Products.id))
    datetime = db.Column(db.DateTime, default=datetime.now())
    
class Referral(db.Model):
    __tablename__ = 'referral'
    id = db.Column(db.Integer, primary_key=True)
    user  = db.relationship(User, backref='referral', lazy=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    product = db.relationship(Products, backref='referral', lazy=True)
    product_id = db.Column(db.Integer(), db.ForeignKey(Products.id))
    
class AdminStats(db.Model):
    __tablename__ = 'admin_stats'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30)) 
    stats = db.Column(db.Integer())
    
class EmailSubcribers(db.Model):
    __tablename__ = 'email_subscriber'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(350))
    date_joined = db.Column(db.DateTime, default=datetime.now())

class ProductAuth(db.Model):
    __tablename__ = 'product_auth'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(200))
    used = db.Column(db.Boolean, default=False)
    product  = db.relationship(Products, backref='Productproducts', lazy=True)
    product_id = db.Column(db.Integer(), db.ForeignKey(Products.id))
    

if __name__ == '__main__':
    manager.run()
