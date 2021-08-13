
# flash
# @app.route("/signup", methds=[o"GET", "POST"])
# def signup():
# # def authenticate_mail():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
    
#     form = MyForm()
#     if request.method == "POST" and form.validate_on_submit():
#         name = form.name.data
#         email = form.email.data
#         phone = form.phone.data
#         password = form.password.data
#         password = md5_crypt.hash(password)
#         user_info = json.dumps({
#             "name": name,
#             "email": email,
#             "phone": phone,
#             "password": password
#         })
#         random_generated = uuid.uuid4()
#         expired_token = time.time() + (int(app.config['TOKEN_EXPIRY_TIME']) * 60 )
#         print((int(app.config['TOKEN_EXPIRY_TIME']) * 60 ))
#         # msg = Message('Hello', sender = 'dataslid@gmail.com', recipients = [email])
#         # msg.body = f"Hello Flask message sent from Flask-Mail, the token is {random_generated}, it expires in {expired_token / 60} hours "
#         # mail.send(msg)
        
#         confirm_user = Confirm_mail(user_details=user_info, token=random_generated, mail=email, dateTime=expired_token )
#         db.session.add(confirm_user)
#         db.session.commit()
        
#         return redirect(url_for("enter_token"))

#     return render_template("sign_up.html", form=form)


@app.route("/enter-token", methods=["GET", "POST"])
# def confirm_mail():
def enter_token():
    if request.method == "POST":
        token_value = request.form.get("token")
        verify_token = Confirm_mail.query.filter_by(token=token_value).first()
        if verify_token:
            current_time = time.time()
            if current_time >= verify_token.dateTime:
                db.session.delete(verify_token)
                db.session.commit()
                # error message
                flash("token has expired, try again")
                return redirect(url_for("confirm_mail"))
                
            else:
                # success msg
                user_data = json.loads(verify_token.user_details)
                user_name = user_data.get("name")
                password = user_data.get("password")
                email = user_data.get("email")
                phone = user_data.get("phone")
    
                password = md5_crypt.hash(password)
                
                user = User(username=user_name, password=password, phone=phone, email=email)
                db.session.add(user)

                delete_confirm = Confirm_mail.query.filter_by(mail=email).all()
                for each_delete_confirm in delete_confirm:
                    db.session.delete(each_delete_confirm)
                db.session.commit()
                

                flash("your account has been verified successfully, you can now login")
                return redirect(url_for("login"))
            print(verify_token.token)
        else:
            flash("token does not exist")
            return redirect(url_for("confirm_mail"))
    else:
        return render_template("enter_token.html")
        
@app.route('/enter-reset-password', methods=["GET", "POST"])
def enter_reset_password():
    form = passwordReset()
    if request.method == "POST" and form.validate_on_submit():
        token_value = request.args.get("token")
        verify_token = Reset_password.query.filter_by(token=token_value).first()
        if verify_token:
            current_time = time.time()
            if current_time >= verify_token.dateTime:
                db.session.delete(verify_token)
                db.session.commit()
                # error message
                flash("token has expired, try again")
                return redirect(f"/enter-reset-password?token={token_value}")
            else:
                # success msg
                password = request.form.get("password")
                password = md5_crypt.hash(password)
                user_id = request.args.get("i")
                user = User.query.filter_by(id=user_id).first()
                user.password = password
                delete_confirm = Reset_password.query.filter_by(mail=user.email).all()
                for each_delete_confirm in delete_confirm:
                    db.session.delete(each_delete_confirm)
                db.session.commit()
                
                flash("You have successfully changed your password")
                return redirect(url_for("login"))
        else:
            flash("token does not exist")
            return redirect(url_for("enter_reset_password"))
    else:
        return render_template('enter_reset_password.html', form=form)


@app.route('/reset-password', methods=["GET", "POST"])
def reset_password():
    # form = passwordResetForm()
    # print(form.validate_on_submit())
    # and form.validate_on_submit()
    if request.method == "POST":
        # email = request.form.get("email")
        email = request.json.get("email")
        user = User.query.filter_by(email=email).first()
        if user:
            random_generated = uuid.uuid4()
            Reset_password.query.filter_by(user_id=user.id).delete()
            
            expired_token = time.time() + (int(app.config['TOKEN_EXPIRY_TIME']) * 60 )
            resetPass = Reset_password(token=random_generated, mail=email, dateTime=expired_token, user_id=user.id)
            db.session.add(resetPass)
            db.session.commit()
            try:
                message = f"Hello Flask message sent from Flask-Mail, the token is {random_generated}, it expires in {expired_token / 60} hours"
                # mail_folks(email, "Reset password from betbots", message)
                msg = Message("Reset password from betbots", sender = 'dataslid@gmail.com', recipients = [email])
                msg.body = render_template('mail_template.txt', message=message)
                msg.html = render_template('mail_template.html', message=message)
                mail.send(msg)
            except Exception as exc:
                print(str(exc))
                return jsonify({"ok": '', "msg": 'Oops! mail failed to send sue to Network issues'})

            # flash("The token has been sent to your mail successfully")
            return jsonify({"ok": 'true', "msg": "The token has been sent to your mail successfully"})
        else:
            return jsonify({'ok': '', 'msg': "E-mail doesn't exist, create an account instead"})
    else:
        return render_template("reset_password.html")

@app.route('/reset-password-confirm')
def confirm_reset_password():
    verify_token = Reset_password.query.filter_by(token=token_value).first()
    if verify_token:
        current_time = time.time()
        if current_time >= verify_token.dateTime:
            db.session.delete(verify_token)
            db.session.commit()
            # error message
            confirm_message = { "failure": "token has expired, try again" }
            return confirm_message

        else:
            confirm_message = { "success": "your account has been verified successfully, you can now change password" }
            return confirm_message

# @app.route('/reset-password-confirm')
# def confirm_reset_password():
#     pass    

    # form = MyForm()
    # if request.method == "POST" and form.validate_on_submit():
    #     password = form.password.data
    #     name = form.name.data
    #     email = form.email.data
    #     phone = form.email.data
    #     password = md5_crypt.hash(password)
    #     check_for_first_user = len(User.query.all())
    #     if not check_for_first_user:
    #         user = User(username=name, is_admin=True, email=email, phone=phone, password=password)
    #     else:
    #         user = User(username=name, is_admin=False, email=email, phone=phone, password=password)
    #     db.session.add(user)
    #     db.session.commit()
    #     flash("You have signed up successfully", "success")    
    #     return redirect('/login')
    # else:
    #     print("HAAAAA")
    # return render_template("sign_up.html", form=form)

   

# @app.route("/download", methods=["GET", "POST"])
# def download():
#     storage_key = os.environ.get("aws_key")
#     storage_secret = os.environ.get("aws_secret")
#     storage_bucket = "betbots"
#     user_id = current_user.id
#     getUser = User.query.get(user_id)
#     conn = boto3.client(
#             's3',
#         aws_access_key_id=storage_key,
#         aws_secret_access_key=storage_secret
#             )
    
#     key = getUser.bet_49ja.bot_path
#     filename = key.split('/')[1]
#     bucket_name = 'betbots'
#     data = conn.get_object(Bucket='betbots', Key=key)
#     # application/zip
#     read_data = data['Body']
#     return send_file(read_data, mimetype='application/x-msdownload', attachment_filename=filename, as_attachment=True)