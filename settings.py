import geoip2.database, csv

from os import getenv, path

ENV = getenv("env")
# ACCEPTED_CURRENCIES = ["GBP", "CAD", "CVE", "CLP",  "COP", "CDF", "EGP", "EUR", "GMD", "GHS", "GNF", "KES", "LRD", "MWK", "MAD", "MZN", "NGN", "SOL", "RWF", "SLL", "STD", "ZAR", "TZS", "UGX", "USD", "XAF", "XOF", "ZMK", "ZMW", "BRL", "MXN", "ARS"]
ACCEPTED_CURRENCIES = ['AED', 'ARS', 'AUD', 'BGN', 'BRL', 'BWP', 'CAD', 'CFA', 'CHF', 'CNY', 'COP', 'CRC', 'CZK', 'DKK', 'EGP', 'EUR', 'GBP', 'GHS', 'HKD', 'HUF', 'ILS', 'INR', 'JPY', 'KES', 'MAD', 'MOP', 'MUR', 'MWK', 'MXN', 'MYR', 'NGN', 'NOK', 'NZD', 'PEN', 'PHP', 'PLN', 'RUB', 'RWF', 'SAR', 'SEK', 'SGD', 'SLL', 'THB', 'TRY', 'TWD', 'TZS', 'UGX', 'USD', 'VEF', 'XAF', 'XOF', 'ZAR', 'ZMK', 'ZMW', 'ZWD']

if ENV == "LIVE":
    PAYSTACK_SECRET = getenv("paystack_live")
else:
    PAYSTACK_SECRET = getenv("paystack_test")

production = getenv("dev")

if production == "live": 
    static_path = path.abspath('./dataslidmarketplace/static')
else:
    static_path = path.abspath('./static')

reader = geoip2.database.Reader(f'{static_path}/GeoLite2-City.mmdb')
csv_file = f'{static_path}/currency.csv'
with open(csv_file, encoding="utf8") as read_file_data:
    csv_list = list(csv.reader(read_file_data, delimiter=","))[1:]
CURRENCIES = {}
for row in csv_list:
    CURRENCIES[row[1]] = row[3]

def check_currency(ip):
    try:
        print("IP addr", ip)
        response = reader.country(ip)
        print("Currency", response.country.iso_code)
        currency_spent = CURRENCIES.get(response.country.iso_code)
        if currency_spent not in ACCEPTED_CURRENCIES:
            currency_spent = "USD"

        return currency_spent
    except Exception as exc:
        print(exc)
        return "USD"

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