# import geoip2.database
from os import getenv, path

ENV = getenv("env")

if ENV == "LIVE":
    PAYSTACK_SECRET = getenv("paystack_live")
else:
    PAYSTACK_SECRET = getenv("paystack_test")

static_path = path.abspath('./static')

# reader = geoip2.database.Reader(f'{static_path}/GeoLite2-City.mmdb')
# # print(cur_path)
# def check_location(ip):
#     try:
#         response = reader.city(ip)
#         return response.country.iso_code
#     # US expection for unknown ip
#     except Exception as exc:
#         return "US"


    # is creates a Reader object. You should use the same object
    # ross multiple requests as creation of it is expensive.
    # Replace "city" with the method corresponding to the database
    # that you are using, e.g., "country".
    # print(response.country.iso_code)
# response.close()
# print(dir(response))
# 'US'
# response.country.name
# 'United States'
# response.country.names['zh-CN']
# u''
# response.subdivisions.most_specific.name
# 'Minnesota'
# response.subdivisions.most_specific.iso_code
# 'MN'
# response.city.name
# 'Minneapolis'
# response.postal.code
# '55455'
# response.location.latitude
# 44.9733
# response.location.longitude
# -93.2323
# response.traits.network
# IPv4Network('203.0.113.0/24')