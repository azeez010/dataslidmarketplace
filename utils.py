import uuid, random
from models import ProductAuth, db
from random import randrange
from botocore.exceptions import ClientError
import boto3, os, re
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
    <body style="padding: 8px ">
        <div style="margin: 5px">
            <p style="font-size: 14px">{message}</p>
            <br>
            <br>
            <a href="https://helpbotics.com/unsubscribe-to-mail?email={RECIPIENT}">Unsubscribe from Newsletter</a>
            <a href="https://helpbotics.com/services">Courtey of Dataslid tech </a>
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

def send_mail(subject, message, recipient):
    try:
        push_email(subject=subject, message=message, recipient=recipient)
        return {"ok": "true"}
    except Exception as exc:
        print(f"fail... {str(exc)}")
        return {"ok": "", "msg": str(exc)}

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

def upload_blog_image(model, obj_key, image):
    if image:
        # Connect with credentials
        storage_key = os.environ.get("aws_key")
        storage_secret = os.environ.get("aws_secret")
        storage_bucket = "myturkeyapp"

        conn = boto3.client(
            's3',
            aws_access_key_id=storage_key,
            aws_secret_access_key=storage_secret
            )

        key_salt = random.randrange(0, 100000)

        filename = image.filename
        Key = f'{obj_key}/{filename}-{key_salt}'
        conn.upload_fileobj(image, storage_bucket, Key)

        image_url = f"https://myturkeyapp.s3.amazonaws.com/{Key}"
        model.image = image_url
        model.image_key = Key
        return image_url
    return None


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

def create_product_key(product_id):
    key = uuid.uuid4()
    if key is None:
        return dict(success=False, message="No key provided"), 400 
    
    product = ProductAuth(key=key, product_id=product_id)
    db.session.add(product)
    db.session.commit()
    
    return dict(success=True, message="Key created"), 200

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

  
  
def validate_email(email):   
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  
  
    if(re.search(regex,email)):   
       return True 
    else:
        return False   