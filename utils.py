import uuid, random, requests, json, boto3, os, re
from models import ProductAuth, Settings, db, CACHE_TIME, CACHE_RATES
from random import randrange
from botocore.exceptions import ClientError
from random import randint
from time import time

# Data
# CACHE_RATES, CACHE_TIME
# CACHE_RATES = {}
# CACHE_TIME = 0

def rate():
    cur_time = time()
    cached_value = Settings.query.filter_by(name="rate").first()
    if cached_value:
        cached_value_json = json.loads(cached_value.value)
        cache_time = cached_value_json.get("time")
        if cur_time > cache_time: 
            res = requests.get("http://data.fixer.io/api/latest?access_key=96c12a99df2b40b46e15f344833c1db7")
            rates = res.json().get("rates")
            values = {
                "time": cur_time + 43200,
                "rates": rates
            }
            cached_value.value = json.dumps(values) 
            db.session.commit()
            return rates
        else:
            cache_rates = cached_value_json.get("rates")
            return cache_rates
    
    else:
        res = requests.get("http://data.fixer.io/api/latest?access_key=96c12a99df2b40b46e15f344833c1db7")
        rates = res.json().get("rates")
        values = {
            "time": cur_time + 43200,
            "rates": rates
        }
        value = json.dumps(values) 
            
        save_rate = Settings(name="rate", value=value)
        db.session.add(save_rate)
        db.session.commit()
        return rates

def change_rate(NGN_rate, to_CUR):
    to_rate = rate().get(to_CUR)
    # NGN is the base Rate
    base_rate = rate().get("NGN")
    euro = 1 / base_rate
    amount = euro * NGN_rate * to_rate 
    return amount

print(change_rate(7250, "USD"))
print(change_rate(7250, "GBP"))
print(change_rate(7250, "NGN"))
print(change_rate(7250, "EUR"))

    
    




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


def all_banks():
    return [{'name': 'Abbey Mortgage Bank', 'slug': 'abbey-mortgage-bank', 'code': '801', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 174, 'createdAt': '2020-12-07T16:19:09.000Z', 'updatedAt': '2020-12-07T16:19:19.000Z'}, {'name': 'Above Only MFB', 'slug': 'above-only-mfb', 'code': '51204', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 188, 'createdAt': '2021-10-13T20:35:17.000Z', 'updatedAt': '2021-10-13T20:35:17.000Z'}, {'name': 'Access Bank', 'slug': 'access-bank', 'code': '044', 'longcode': '044150149', 'gateway': 'emandate', 'pay_with_bank': 
False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 1, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T08:06:44.000Z'}, {'name': 'Access Bank (Diamond)', 'slug': 'access-bank-diamond', 'code': 
'063', 'longcode': '063150162', 'gateway': 'emandate', 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 3, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T08:06:48.000Z'}, {'name': 'ALAT by WEMA', 'slug': 'alat-by-wema', 'code': '035A', 'longcode': 
'035150103', 'gateway': 'emandate', 'pay_with_bank': True, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 27, 'createdAt': '2017-11-15T12:21:31.000Z', 'updatedAt': '2021-02-18T14:55:34.000Z'}, {'name': 'Amju Unique MFB', 'slug': 'amju-unique-mfb', 'code': '50926', 'longcode': '511080896', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 179, 'createdAt': '2021-07-07T13:45:57.000Z', 'updatedAt': '2021-07-07T13:45:57.000Z'}, {'name': 'ASO Savings and Loans', 'slug': 'asosavings', 'code': '401', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 63, 'createdAt': '2018-09-23T05:52:38.000Z', 'updatedAt': '2019-01-30T09:38:57.000Z'}, {'name': 'Bainescredit MFB', 'slug': 'bainescredit-mfb', 'code': '51229', 'longcode': '', 'gateway': 
None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 181, 'createdAt': '2021-07-12T14:41:18.000Z', 'updatedAt': '2021-07-12T14:41:18.000Z'}, {'name': 'Bowen Microfinance Bank', 'slug': 'bowen-microfinance-bank', 'code': '50931', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 108, 'createdAt': '2020-02-11T15:38:57.000Z', 'updatedAt': '2020-02-11T15:38:57.000Z'}, {'name': 'Carbon', 'slug': 'carbon', 'code': '565', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 82, 'createdAt': '2020-06-16T08:15:31.000Z', 'updatedAt': '2021-08-05T15:25:01.000Z'}, {'name': 'CEMCS Microfinance Bank', 'slug': 'cemcs-microfinance-bank', 'code': '50823', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 74, 'createdAt': '2020-03-23T15:06:13.000Z', 
'updatedAt': '2020-03-23T15:06:28.000Z'}, {'name': 'Chanelle Microfinance Bank Limited', 'slug': 'chanelle-microfinance-bank-limited-ng', 'code': '50171', 'longcode': '50171', 'gateway': '', 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 284, 'createdAt': '2022-02-10T13:28:38.000Z', 'updatedAt': '2022-02-10T13:28:38.000Z'}, {'name': 'Citibank Nigeria', 'slug': 'citibank-nigeria', 'code': '023', 'longcode': '023150005', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 2, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T20:24:02.000Z'}, {'name': 'Corestep MFB', 'slug': 'corestep-mfb', 'code': '50204', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 283, 'createdAt': '2022-02-09T14:33:06.000Z', 'updatedAt': '2022-02-09T14:33:06.000Z'}, {'name': 'Coronation Merchant Bank', 'slug': 'coronation-merchant-bank', 'code': '559', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 173, 'createdAt': '2020-11-24T10:25:07.000Z', 'updatedAt': '2020-11-24T10:25:07.000Z'}, {'name': 'Ecobank Nigeria', 'slug': 'ecobank-nigeria', 'code': '050', 'longcode': '050150010', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 4, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T20:23:53.000Z'}, {'name': 'Ekondo Microfinance Bank', 'slug': 'ekondo-microfinance-bank', 'code': '562', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 64, 'createdAt': '2018-09-23T05:55:06.000Z', 'updatedAt': '2018-09-23T05:55:06.000Z'}, {'name': 'Eyowo', 'slug': 'eyowo', 'code': '50126', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': 
False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 167, 
'createdAt': '2020-09-07T13:52:22.000Z', 'updatedAt': '2020-11-24T10:03:21.000Z'}, {'name': 'Fidelity Bank', 'slug': 'fidelity-bank', 'code': '070', 'longcode': '070150003', 'gateway': 'emandate', 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 6, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2021-08-27T09:15:29.000Z'}, {'name': 'Firmus MFB', 'slug': 'firmus-mfb', 'code': '51314', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 177, 'createdAt': '2021-06-01T15:33:26.000Z', 'updatedAt': '2021-06-01T15:33:26.000Z'}, {'name': 'First Bank of Nigeria', 'slug': 'first-bank-of-nigeria', 'code': '011', 'longcode': '011151003', 'gateway': 'ibank', 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 
'Nigeria', 'currency': 'NGN', 'type': 
'nuban', 'id': 7, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2021-03-25T14:22:52.000Z'}, {'name': 'First City Monument Bank', 'slug': 'first-city-monument-bank', 'code': '214', 'longcode': '214150018', 'gateway': 'emandate', 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 8, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': 
'2020-02-18T08:06:46.000Z'}, {'name': 
'FSDH Merchant Bank Limited', 'slug': 
'fsdh-merchant-bank-limited', 'code': 
'501', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 112, 'createdAt': '2020-08-20T09:37:04.000Z', 'updatedAt': '2020-11-24T10:03:22.000Z'}, {'name': 'Gateway Mortgage Bank LTD', 'slug': 'gateway-mortgage-bank', 'code': '812', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 287, 'createdAt': '2022-02-24T06:04:39.000Z', 'updatedAt': '2022-02-24T06:04:39.000Z'}, {'name': 'Globus Bank', 
'slug': 'globus-bank', 'code': '00103', 'longcode': '103015001', 'gateway': 
None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 70, 'createdAt': '2020-02-11T15:38:57.000Z', 'updatedAt': '2020-02-11T15:38:57.000Z'}, {'name': 'GoMoney', 'slug': 'gomoney', 'code': '100022', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': 
True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 183, 'createdAt': '2021-08-04T11:49:46.000Z', 'updatedAt': '2021-11-12T13:32:14.000Z'}, {'name': 'Guaranty Trust Bank', 'slug': 'guaranty-trust-bank', 'code': '058', 'longcode': '058152036', 'gateway': 'ibank', 'pay_with_bank': True, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 
'id': 9, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2021-01-01T11:22:11.000Z'}, {'name': 'Hackman Microfinance Bank', 'slug': 'hackman-microfinance-bank', 'code': '51251', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 
111, 'createdAt': '2020-08-20T09:32:48.000Z', 'updatedAt': '2020-11-24T10:03:24.000Z'}, {'name': 'Hasal Microfinance Bank', 'slug': 'hasal-microfinance-bank', 'code': '50383', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 
'NGN', 'type': 'nuban', 'id': 81, 'createdAt': '2020-02-11T15:38:57.000Z', 'updatedAt': '2020-02-11T15:38:57.000Z'}, {'name': 'Heritage Bank', 'slug': 'heritage-bank', 'code': '030', 'longcode': '030159992', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 10, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T20:24:23.000Z'}, {'name': 'Ibile Microfinance Bank', 'slug': 'ibile-mfb', 'code': '51244', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 168, 'createdAt': '2020-10-21T10:54:20.000Z', 'updatedAt': '2020-10-21T10:54:33.000Z'}, {'name': 'Infinity MFB', 'slug': 'infinity-mfb', 'code': '50457', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 
'NGN', 'type': 'nuban', 'id': 172, 'createdAt': '2020-11-24T10:23:37.000Z', 
'updatedAt': '2020-11-24T10:23:37.000Z'}, {'name': 'Jaiz Bank', 'slug': 'jaiz-bank', 'code': '301', 'longcode': '301080020', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 
22, 'createdAt': '2016-10-10T17:26:29.000Z', 'updatedAt': '2016-10-10T17:26:29.000Z'}, {'name': 'Kadpoly MFB', 'slug': 'kadpoly-mfb', 'code': '50502', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 
'currency': 'NGN', 'type': 'nuban', 'id': 187, 'createdAt': '2021-09-27T11:59:42.000Z', 'updatedAt': '2021-09-27T11:59:42.000Z'}, {'name': 'Keystone Bank', 'slug': 'keystone-bank', 'code': '082', 'longcode': '082150017', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 11, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T20:23:45.000Z'}, {'name': 'Kredi Money MFB LTD', 'slug': 'kredi-money-mfb', 'code': '50200', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 184, 'createdAt': '2021-08-11T09:54:03.000Z', 'updatedAt': '2021-08-11T09:54:03.000Z'}, {'name': 'Kuda Bank', 'slug': 'kuda-bank', 'code': '50211', 'longcode': '', 'gateway': 'digitalbankmandate', 'pay_with_bank': True, 'active': 
True, 'is_deleted': False, 'country': 
'Nigeria', 'currency': 'NGN', 'type': 
'nuban', 'id': 67, 'createdAt': '2019-11-15T17:06:54.000Z', 'updatedAt': '2020-07-01T15:05:18.000Z'}, {'name': 'Lagos Building Investment Company Plc.', 'slug': 'lbic-plc', 'code': '90052', 
'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 
'id': 109, 'createdAt': '2020-08-10T15:07:44.000Z', 'updatedAt': '2020-08-10T15:07:44.000Z'}, {'name': 'Links MFB', 'slug': 'links-mfb', 'code': '50549', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 180, 'createdAt': '2021-07-12T14:41:18.000Z', 'updatedAt': '2021-07-12T14:41:18.000Z'}, {'name': 'Lotus Bank', 'slug': 'lotus-bank', 'code': '303', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 
'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 233, 'createdAt': '2021-12-06T14:39:51.000Z', 'updatedAt': '2021-12-06T14:39:51.000Z'}, {'name': 'Mayfair MFB', 'slug': 'mayfair-mfb', 'code': '50563', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 175, 'createdAt': '2021-02-02T08:28:38.000Z', 'updatedAt': '2021-02-02T08:28:38.000Z'}, {'name': 'Mint MFB', 'slug': 'mint-mfb', 'code': '50304', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 178, 'createdAt': '2021-06-01T16:07:29.000Z', 'updatedAt': '2021-06-01T16:07:29.000Z'}, {'name': 'Paga', 'slug': 'paga', 'code': '100002', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 
'currency': 'NGN', 'type': 'nuban', 'id': 185, 'createdAt': '2021-08-31T08:10:00.000Z', 'updatedAt': '2021-08-31T08:10:00.000Z'}, {'name': 'PalmPay', 'slug': 'palmpay', 'code': '999991', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 169, 'createdAt': '2020-11-24T09:58:37.000Z', 'updatedAt': '2020-11-24T10:03:19.000Z'}, {'name': 'Parallex Bank', 'slug': 'parallex-bank', 'code': '104', 'longcode': '', 'gateway': None, 
'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 26, 'createdAt': '2017-03-31T13:54:29.000Z', 'updatedAt': '2021-10-29T08:00:19.000Z'}, {'name': 'Parkway - ReadyCash', 'slug': 'parkway-ready-cash', 'code': '311', 'longcode': '', 
'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 110, 'createdAt': '2020-08-10T15:07:44.000Z', 'updatedAt': '2020-08-10T15:07:44.000Z'}, {'name': 'Paycom', 'slug': 'paycom', 'code': '999992', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 
'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 171, 'createdAt': '2020-11-24T10:20:45.000Z', 'updatedAt': '2020-11-24T10:20:54.000Z'}, {'name': 'Petra Mircofinance Bank Plc', 'slug': 'petra-microfinance-bank-plc', 'code': '50746', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 
'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 170, 'createdAt': '2020-11-24T10:03:06.000Z', 'updatedAt': '2020-11-24T10:03:06.000Z'}, {'name': 'Polaris Bank', 'slug': 'polaris-bank', 'code': '076', 'longcode': '076151006', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 13, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2016-07-14T10:04:29.000Z'}, {'name': 'Providus Bank', 
'slug': 'providus-bank', 'code': '101', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 25, 'createdAt': '2017-03-27T16:09:29.000Z', 'updatedAt': '2021-02-09T17:50:06.000Z'}, {'name': 'QuickFund MFB', 'slug': 'quickfund-mfb', 'code': '51293', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 
'Nigeria', 'currency': 'NGN', 'type': 
'nuban', 'id': 232, 'createdAt': '2021-10-29T08:43:35.000Z', 'updatedAt': '2021-10-29T08:43:35.000Z'}, {'name': 'Rand Merchant Bank', 'slug': 'rand-merchant-bank', 'code': '502', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': 
None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 176, 'createdAt': '2021-02-11T17:33:20.000Z', 'updatedAt': '2021-02-11T17:33:20.000Z'}, {'name': 'Rubies MFB', 'slug': 'rubies-mfb', 'code': '125', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 69, 
'createdAt': '2020-01-25T09:49:59.000Z', 'updatedAt': '2020-01-25T09:49:59.000Z'}, {'name': 'Safe Haven MFB', 'slug': 'safe-haven-mfb-ng', 'code': '51113', 'longcode': '51113', 'gateway': '', 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 286, 'createdAt': '2022-02-18T13:11:59.000Z', 'updatedAt': '2022-02-18T13:11:59.000Z'}, {'name': 'Sparkle Microfinance Bank', 'slug': 'sparkle-microfinance-bank', 'code': '51310', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 
'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 72, 'createdAt': '2020-02-11T18:43:14.000Z', 'updatedAt': '2020-02-11T18:43:14.000Z'}, {'name': 'Stanbic IBTC Bank', 'slug': 'stanbic-ibtc-bank', 'code': '221', 'longcode': '221159522', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': 
None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 14, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T20:24:17.000Z'}, {'name': 'Standard Chartered Bank', 'slug': 'standard-chartered-bank', 
'code': '068', 'longcode': '068150015', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 15, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T20:23:40.000Z'}, {'name': 'Stellas MFB', 'slug': 'stellas-mfb', 'code': '51253', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 285, 
'createdAt': '2022-02-17T14:54:01.000Z', 'updatedAt': '2022-02-17T14:54:01.000Z'}, {'name': 'Sterling Bank', 'slug': 'sterling-bank', 'code': '232', 'longcode': '232150016', 'gateway': 'emandate', 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 16, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2021-11-02T20:35:10.000Z'}, {'name': 'Suntrust Bank', 'slug': 'suntrust-bank', 'code': '100', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 
'type': 'nuban', 'id': 23, 'createdAt': '2016-10-10T17:26:29.000Z', 'updatedAt': '2016-10-10T17:26:29.000Z'}, {'name': 'TAJ Bank', 'slug': 'taj-bank', 'code': '302', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 68, 'createdAt': '2020-01-20T11:20:32.000Z', 'updatedAt': '2020-01-20T11:20:32.000Z'}, {'name': 'Tangerine Money', 'slug': 'tangerine-money', 'code': '51269', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': 
None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 186, 'createdAt': '2021-09-17T13:25:16.000Z', 'updatedAt': '2021-09-17T13:25:16.000Z'}, {'name': 'TCF MFB', 'slug': 'tcf-mfb', 'code': '51211', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 
'NGN', 'type': 'nuban', 'id': 75, 'createdAt': '2020-04-03T09:34:35.000Z', 'updatedAt': '2020-04-03T09:34:35.000Z'}, {'name': 'Titan Bank', 'slug': 'titan-bank', 'code': '102', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 73, 'createdAt': '2020-03-10T11:41:36.000Z', 
'updatedAt': '2020-03-23T15:06:29.000Z'}, {'name': 'Unical MFB', 'slug': 'unical-mfb', 'code': '50871', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 282, 
'createdAt': '2022-01-10T09:52:47.000Z', 'updatedAt': '2022-01-10T09:52:47.000Z'}, {'name': 'Union Bank of Nigeria', 'slug': 'union-bank-of-nigeria', 'code': '032', 'longcode': '032080474', 
'gateway': 'emandate', 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 17, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2020-02-18T20:22:54.000Z'}, {'name': 'United Bank For Africa', 'slug': 'united-bank-for-africa', 'code': '033', 'longcode': '033153513', 'gateway': 'emandate', 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 18, 
'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2022-03-09T10:28:57.000Z'}, {'name': 'Unity Bank', 'slug': 
'unity-bank', 'code': '215', 'longcode': '215154097', 'gateway': 'emandate', 'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 19, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2019-07-22T12:44:02.000Z'}, {'name': 'VFD Microfinance Bank Limited', 'slug': 'vfd', 'code': '566', 'longcode': '', 'gateway': None, 'pay_with_bank': False, 'active': True, 'is_deleted': False, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 71, 'createdAt': '2020-02-11T15:44:11.000Z', 'updatedAt': '2020-10-28T09:42:08.000Z'}, {'name': 'Wema Bank', 'slug': 'wema-bank', 'code': '035', 'longcode': '035150103', 'gateway': None, 'pay_with_bank': 
False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 20, 'createdAt': '2016-07-14T10:04:29.000Z', 
'updatedAt': '2021-02-09T17:49:59.000Z'}, {'name': 'Zenith Bank', 'slug': 'zenith-bank', 'code': '057', 'longcode': '057150013', 'gateway': 'emandate', 
'pay_with_bank': False, 'active': True, 'is_deleted': None, 'country': 'Nigeria', 'currency': 'NGN', 'type': 'nuban', 'id': 21, 'createdAt': '2016-07-14T10:04:29.000Z', 'updatedAt': '2022-03-16T10:15:29.000Z'
}]