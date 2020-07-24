import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://api.krispykreme.com/shops/?latitude=40&longitude=-90&count=5000&shopFeatureFlags=0&includeGroceryStores=false&includeShops=true'
    r = session.get(url, headers=headers)
    website = 'krispykreme.com'
    typ = '<MISSING>'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"siteId":' in line:
            items = line.split('{"siteId":')
            for item in items:
                if '"shopId":' in item:
                    name = item.split('"shopName":"')[1].split('"')[0]
                    store = item.split('"shopId":')[1].split(',')[0]
                    loc = 'https://www.krispykreme.com' + item.split('"shopUrl":"')[1].split('"')[0]
                    add = item.split('"address1":"')[1].split('"')[0] + ' ' + item.split('"address2":"')[1].split('"')[0]
                    add = add.strip()
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"zipCode":"')[1].split('"')[0]
                    country = 'US'
                    phone = item.split('"phoneNumber":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    hours = item.split('"shortHoursHotlight":[{"key":"')[1].split('"')[0] + '; ' + item.split('"shortHoursHotlight":[{"key":"')[1].split(',"value":"')[1].split('"')[0]
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
