from flask_login import current_user 
from models import User, app, db
from random import randrange
from botocore.exceptions import ClientError
import boto3, os, time
from flask import request, render_template, jsonify
from random import randint


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
        storage_bucket = "dataslid"
        
        # Set Expiry time
        conn = boto3.client(
            's3',
            aws_access_key_id=storage_key,
            aws_secret_access_key=storage_secret
            )

        # delete object
        conn.delete_object(Bucket=storage_bucket, Key=Key)

def upload_image(model, image, upload_type):
    if image:
        # Connect with credentials
        storage_key = os.environ.get("aws_key")
        storage_secret = os.environ.get("aws_secret")
        storage_bucket = "dataslid"

        conn = boto3.client(
            's3',
            aws_access_key_id=storage_key,
            aws_secret_access_key=storage_secret
            )

        key_salt = randrange(0, 100000)

        filename = image.filename
        Key = f'{upload_type}/{filename}-{key_salt}'
        conn.upload_fileobj(image, storage_bucket, Key)

        upload_url = f"https://{storage_bucket}.s3.amazonaws.com/{Key}"
        
        print(upload_type)
        # elif upload_type == "thumbnail":
        #     model.image = upload_url
        #     model.image_key = Key
        if upload_type == "image":
            model.thumbnail = upload_url
            model.thumbnail_key = Key
        
        elif upload_type == "demo":
            model.demo_link = upload_url
            model.demo_key = Key
        
        elif upload_type == "download":
            model.download_link = upload_url
            model.download_key = Key
        

        

def send_message_to_admins(Subject, notes):
    # Get all admin id
    admins = User.query.filter_by(is_admin=True).all()
    
    # Send notes to all admin
    for admin in admins:
        check = send_inbox_message(admin.id, notes)
        # Check if sent to app mail box
        if check[0]:
            send_mail(subject=Subject, message=notes, recipient=admin.email)

def get_two_random_number(len_of_products):
    product_len = len_of_products
    slice_range = 4
    end = randint(0, product_len)
    
    if slice_range > end:
        end += slice_range
        
        if product_len < slice_range:
            slice_range = product_len 

        if end > product_len:
            diff = end - product_len 
            end -= diff

        
    start = end - slice_range
    return start, end
