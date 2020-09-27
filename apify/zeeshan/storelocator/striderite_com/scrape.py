import csv
import requests
import os

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

HEADERS = {
    'Referer': 'https://www.striderite.com/en/stores',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

URL = "https://storerocket.global.ssl.fastly.net/api/user/wjN49rzJGy/locations?lat=37.7802277&lng=-122.40416580000002&radius=500000" 

session = requests.Session()
##proxy_password = os.environ["PROXY_PASSWORD"]
##proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
##proxies = {
##    'http': proxy_url,
##    'https': proxy_url
##}
##session.proxies = proxies

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def fetch_data():
    stores = []
    results = session.get(URL, headers=HEADERS).json()['results']['locations']
    for result in results:
        location_name = result['name'].replace('"',"'")
        locator_domain = 'striderite.com'
        page_url = handle_missing(str(result['url']))
        store_number = handle_missing(result['id'])
        street_address = handle_missing(result['address_line_1'])
        if len(result['address_line_2']) > 0:
            street_address += ' ' + result['address_line_2']
        latitude = handle_missing(result['lat'])
        longitude = handle_missing(result['lng'])
        city = handle_missing(result['city'])
        state = handle_missing(result['state'])
        zip_code = handle_missing(result['postcode'])
        country_code = handle_missing(result['country'])
        location_type = handle_missing(result['location_type_name'])
        phone = handle_missing(result['phone'])
        hours_of_operation = '<MISSING>' if len(result['hours']) == 0 or not result['hours']['mon'] else result['hours']
        hours = str(hours_of_operation)
        hours = hours
        stores.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours])
    return stores

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
