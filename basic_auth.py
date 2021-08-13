from models import UserProducts, db, app, EmailSubcribers, Confirm_mail, Transaction_Table, User, Reset_password, current_user, Make_request, Store, Products, ProductImage, Referral
from flask import url_for, request, render_template, redirect, flash, send_from_directory, send_file, jsonify, Response
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView



from flask_admin import Admin
from flask_admin.contrib import sqla as flask_admin_sqla
from flask_admin import AdminIndexView
from flask_admin import expose
from flask_admin.menu import MenuLink


class DefaultModelView(flask_admin_sqla.ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    @expose('/')
    def index(self):
        if not current_user.is_authenticated and current_user.is_admin:
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

# further in app.py
admin = Admin(
        app,
        name='My App',
        # template_mode='bootstrap4',
        index_view=MyAdminIndexView()
    )

# admin.add_view(DefaultModelView(Predictions, db.session))
admin.add_link(MenuLink(name='Logout', category='', url='/logout?next=/admin'))

admin.add_view(DefaultModelView(Transaction_Table, db.session))
admin.add_view(DefaultModelView(User, db.session))
admin.add_view(DefaultModelView(Store, db.session))
admin.add_view(DefaultModelView(Products, db.session))
admin.add_view(DefaultModelView(ProductImage, db.session))
admin.add_view(DefaultModelView(Referral, db.session))
admin.add_view(DefaultModelView(UserProducts, db.session))
admin.add_view(DefaultModelView(Make_request, db.session))
admin.add_view(DefaultModelView(EmailSubcribers, db.session))