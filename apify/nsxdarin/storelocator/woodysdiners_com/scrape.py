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
    url = 'https://www.woodysdiners.com/locations'
    r = session.get(url, headers=headers)
    website = 'woodysdiners.com'
    typ = 'Restaurant'
    country = 'US'
    loc = '<MISSING>'
    store = '<MISSING>'
    hours = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"__typename":"CustomForm","id":11687,"allowAttachments":false,"des' in line:
            items = line.split('{"__typename":"CustomForm","id":11687,"allowAttachments":false,"des')[1].split('"RestaurantLocation","id":')
            for item in items:
                if '"allowReservations":' in item:
                    loc = 'https://www.woodysdiners.com/' + item.split('"slug":"')[1].split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    lat = item.split(',"lat":')[1].split(',')[0]
                    lng = item.split(',"lng":')[1].split(',')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    hours = item.split(',"schemaHours":["')[1].split(']')[0].replace('","','; ').replace('"','')
                    state = item.split('"state":"')[1].split('"')[0]
                    add = item.split('"streetAddress":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    store = item.split(',')[0]
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
