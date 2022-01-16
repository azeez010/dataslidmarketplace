from models import app, db, ProductAuth
from flask import request

@app.route("/check-product-key", methods=["GET"])
def product_key():
    key = request.args.get("key")
    if key is None:
        return dict(success=False, message="No key provided"), 400 
    
    product = ProductAuth.query.filter_by(key=key, used=False).first()

    if product is None:
        return dict(success=False, message="Invalid key"), 400
    
    return dict(success=True, message="Valid key"), 200

@app.route("/confirm-product-key", methods=["POST"])
def confirm_product_key():
    key = request.form.get("key")
    
    if key is None:
        return dict(success=False, message="No key provided"), 400 
    
    product = ProductAuth.query.filter_by(key=key, used=False).first()

    if product is None:
        return dict(success=False, message="Invalid key"), 400
    
    product.used = True
    db.session.commit()

    return dict(success=True, key=product.key, message="Valid key"), 200