from flask_login import current_user 
from models import User, app, db
from botocore.exceptions import ClientError
import boto3, os, time



from flask import request, render_template, jsonify

# def get_aws_url(product):
#     storage_key = os.environ.get("aws_key")
#     storage_secret = os.environ.get("aws_secret")
#     storage_bucket = "myturkeyapp"
#     urlExpiryTime = 604799
#     download_expiry_time = time.time() + urlExpiryTime
#     conn = boto3.client(
#         's3',
#         aws_access_key_id=storage_key,
#         aws_secret_access_key=storage_secret
#         )
    
    # if "<class 'list'>" == str(type(product)) and len(product) > 0:
    #     for _product in product:
#             current_time = time.time()
#             expiry_time = _product.s3_expiry_time
#             if not expiry_time:
#                 expiry_time = 0

#             if current_time > expiry_time:
#                 if _product.download_link:
#                     Key = _product.download_key    
#                     download_link = conn.generate_presigned_url(ClientMethod='get_object', Params={
#                     'Bucket': storage_bucket,
#                     'Key': Key
#                 }, ExpiresIn=urlExpiryTime)
#                     _product.download_link = download_link


#                 if _product.demo_link:
#                     Key = _product.download_key    
#                     demo_link = conn.generate_presigned_url(ClientMethod='get_object', Params={
#                     'Bucket': storage_bucket,
#                     'Key': Key
#                 }, ExpiresIn=urlExpiryTime)

#                     _product.demo_link = demo_link

#                 if _product.thumbnail:
#                     Key = _product.download_key    
#                     thumbnail = conn.generate_presigned_url(ClientMethod='get_object', Params={
#                     'Bucket': storage_bucket,
#                     'Key': Key
#                 }, ExpiresIn=urlExpiryTime)

#                     _product.thumbnail = thumbnail
#             _product.s3_expiry_time = download_expiry_time
#             db.session.commit()
#     else:
#         current_time = time.time()
#         expiry_time = product.s3_expiry_time     
#         if current_time > expiry_time:
#             if product.download_link:
#                 Key = product.download_key    
#                 download_link = conn.generate_presigned_url(ClientMethod='get_object', Params={
#                 'Bucket': storage_bucket,
#                 'Key': Key
#             }, ExpiresIn=urlExpiryTime)

#             product.download_link = download_link

#             if product.demo_link:
#                 Key = product.download_key    
#                 demo_link = conn.generate_presigned_url(ClientMethod='get_object', Params={
#                 'Bucket': storage_bucket,
#                 'Key': Key
#             }, ExpiresIn=urlExpiryTime)

#             product.demo_link = demo_link

#             if product.thumbnail:
#                 Key = product.download_key    
#                 thumbnail = conn.generate_presigned_url(ClientMethod='get_object', Params={
#                 'Bucket': storage_bucket,
#                 'Key': Key
#             }, ExpiresIn=urlExpiryTime)

#             product.thumbnail = thumbnail

#         product.s3_expiry_time = download_expiry_time
#         db.session.commit()

def get_image_url(product):
    storage_key = os.environ.get("aws_key")
    storage_secret = os.environ.get("aws_secret")
    storage_bucket = "myturkeyapp"
    urlExpiryTime = 604799
    url_expiry_time = time.time() + urlExpiryTime
    current_time = time.time()
    
    conn = boto3.client(
        's3',
        aws_access_key_id=storage_key,
        aws_secret_access_key=storage_secret
        )
    if product:
        if "<class 'list'>" == str(type(product)) and len(product) > 0:
            for _product in product:
                current_time = time.time()
                expiry_time = _product.s3_expiry_time
                if not expiry_time:
                    expiry_time = 0

                if current_time > expiry_time and _product.image_key:
                    Key = _product.image_key    
                    thumbnail = conn.generate_presigned_url(ClientMethod='get_object', Params={
                    'Bucket': storage_bucket,
                    'Key': Key
                }, ExpiresIn=urlExpiryTime)

                    _product.image_url = thumbnail
                    _product.s3_expiry_time = url_expiry_time
                    db.session.commit()
        else:
            current_time = time.time()
            expiry_time = product.s3_expiry_time     
            
            if current_time > expiry_time:
                Key = product.image_key    
                image_url = conn.generate_presigned_url(ClientMethod='get_object', Params={
                'Bucket': storage_bucket,
                'Key': Key
            }, ExpiresIn=urlExpiryTime)

                product.image_url = image_url
                product.s3_expiry_time = url_expiry_time
                db.session.commit()

def get_profile_url():
    storage_key = os.environ.get("aws_key")
    storage_secret = os.environ.get("aws_secret")
    storage_bucket = "myturkeyapp"
    urlExpiryTime = 604799
    url_expiry_time = time.time() + urlExpiryTime
    current_time = time.time()

    pic_expiry = current_user.s3_expiry_time
    
    # Run this when pictures expires
    if current_time > pic_expiry:
        conn = boto3.client(
            's3',
            aws_access_key_id=storage_key,
            aws_secret_access_key=storage_secret
            )
        
        Key = current_user.thumbnail_key
        image_url = conn.generate_presigned_url(ClientMethod='get_object', Params={
            'Bucket': storage_bucket,
            'Key': Key
        }, ExpiresIn=urlExpiryTime)

        current_user.thumbnail_url = image_url
        current_user.s3_expiry_time = url_expiry_time

def get_product_url(product):
    print(product, "!!!")
    if product:

        print(product, "Came here")
        storage_key = os.environ.get("aws_key")
        storage_secret = os.environ.get("aws_secret")
        storage_bucket = "myturkeyapp"
        urlExpiryTime = 604799
        url_expiry_time = time.time() + urlExpiryTime
        current_time = time.time()
        
        conn = boto3.client(
            's3',
            aws_access_key_id=storage_key,
            aws_secret_access_key=storage_secret
            )

        if "<class 'list'>" == str(type(product)) and len(product) > 0:

            print("Hello too")
            for _product in product:
                current_time = time.time()
                expiry_time = _product.s3_expiry_time
                if not expiry_time:
                    expiry_time = 0

                print(current_time, expiry_time, _product.thumbnail_key)
                if current_time > expiry_time  and _product.thumbnail_key:
                    Key = _product.thumbnail_key    
                    thumbnail = conn.generate_presigned_url(ClientMethod='get_object', Params={
                    'Bucket': storage_bucket,
                    'Key': Key
                }, ExpiresIn=urlExpiryTime)
                    print(thumbnail)
                    _product.thumbnail_url = thumbnail
                    _product.s3_expiry_time = url_expiry_time
                    db.session.commit()
        else:
            current_time = time.time()
            expiry_time = product.s3_expiry_time     
            
            if current_time > expiry_time and product.thumbnail_key:
                Key = product.download_key    
                thumbnail_url = conn.generate_presigned_url(ClientMethod='get_object', Params={
                'Bucket': storage_bucket,
                'Key': Key
            }, ExpiresIn=urlExpiryTime)

                product.thumbnail_url = thumbnail_url
                product.s3_expiry_time = url_expiry_time
                db.session.commit()

def push_email(recipient, subject, message):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = f"My Turkey app <{os.environ.get('email')}>"
    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = recipient #"azeezolabode010@gmail.com"

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = subject #"Bet9ja Virtual League Notification"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = message 
    # ("Automated message from Amazon SES (Python)\r\n"
    #             "This email was sent with Amazon SES using the "
    #             "AWS SDK for Python (Boto)."
    #             )
                
    # The HTML body of the email.
    BODY_HTML = f"""<html>
    <head></head>
    <body style="background-color: #ccc; padding: 8px ">
        <div style="background-color: #fff">
            <h1>{subject}</h1>
            <p style="font-size: 16px">{message}</p>
            <br>
            <br>
            <a href="dataslid.pythonanywhere.com">Courtey of Dataslid tech </a>
        </div>
    </body>
    </html>
                """            

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    email_key = os.environ.get("aws_key")
    email_secret = os.environ.get("aws_secret")
    client = boto3.client('ses',region_name=AWS_REGION, aws_access_key_id=email_key, aws_secret_access_key=email_secret)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
# class Utils():

def send_mail(subject, message, recipient):
    try:
        push_email(subject=subject, message=message, recipient=recipient)
        return {"ok": "true"}
    except Exception as exc:
        print(f"fail... {str(exc)}")
        return {"ok": "", "msg": str(exc)}

def send_inbox_message(user_id, message):
    try:
        inbox = Inbox(message=message, user_id=user_id)
        db.session.add(inbox)
        db.session.commit()
        return True, inbox.id
    except Exception as e:
        return False 


# @app.route("/mail-users", methods=["POST"])
# def mail_user():
#     # Senders Mail
#     sender_email = os.environ.get("email")
#     user_id = int(request.json.get("user_id"))
#     # Receiver Mail
#     recipient = request.json.get("user")
#     message = request.json.get("message")
#     subject = request.json.get("subject")
#     print(recipient)
#     try:
#         push_email(subject=subject, message=message, recipient=recipient)
#         send_inbox_message(user_id=user_id, message=message)
#         return {"ok": "true"}
#     except Exception as exc:
#         print(f"fail... {str(exc)}")
#         return {"ok": "", "msg": str(exc)}

def delete_image(Key):
    if Key:
        storage_key = os.environ.get("aws_key")
        storage_secret = os.environ.get("aws_secret")
        storage_bucket = "myturkeyapp"
        
        # Set Expiry time
        conn = boto3.client(
            's3',
            aws_access_key_id=storage_key,
            aws_secret_access_key=storage_secret
            )

        # delete object
        conn.delete_object(Bucket=storage_bucket, Key=Key)

def upload_image(model, image):
    if image:
        # Connect with credentials
        storage_key = os.environ.get("aws_key")
        storage_secret = os.environ.get("aws_secret")
        storage_bucket = "myturkeyapp"
        urlExpiryTime = 604799
        download_expiry_time = time.time() + urlExpiryTime
        
        # Set Expiry time
        model.s3_expiry_time = download_expiry_time

        conn = boto3.client(
            's3',
            aws_access_key_id=storage_key,
            aws_secret_access_key=storage_secret
            )

        filename = image.filename
        Key = f'store/{filename}'
        conn.upload_fileobj(image, storage_bucket, Key)


        image_url = conn.generate_presigned_url(ClientMethod='get_object', Params={
            'Bucket': storage_bucket,
            'Key': Key
        }, ExpiresIn=urlExpiryTime)

        model.image = image_url
        model.image_key = Key

def send_message_to_admins(Subject, notes):
    # Get all admin id
    admins = User.query.filter_by(is_admin=True).all()
    
    # Send notes to all admin
    for admin in admins:
        check = send_inbox_message(admin.id, notes)
        # Check if sent to app mail box
        if check[0]:
            send_mail(subject=Subject, message=notes, recipient=admin.email)

# def notification_note(name):
#     return f"""
#             {title} by {name}
#             <hr />
#             {notes}
#             <br />  
#             <a href='{site_name}pairing-group?id={pairing_group.id}'>Click link to check the pairing group request</a>
#             <br />
#             <hr />
#             Phone: {phone}
#         """