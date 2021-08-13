from models import User, db, app, Make_request
from flask_marshmallow import Marshmallow
ma = Marshmallow(app)

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        model = User
        fields = ("id","username", "email", "is_admin", "phone", "is_paid")


class MakeRequest(ma.Schema):
    class Meta:
        # Fields to expose
        model = Make_request
        fields = ("id","user.username", "request", "datetime")

user_schema = UserSchema(many=True)
request_schema = MakeRequest(many=True)