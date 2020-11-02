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
    url = 'https://pacsys.marriott.com/data/marriott_properties_LC_en-US.json'
    r = session.get(url, headers=headers)
    website = 'the-luxury-collection.marriott.com'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"region_id":"north.america"' in line:
            items = line.split('{"region_id":"north.america"')[1].split(']}]}]}]},')[0].split('{"marsha_code":"')
            for item in items:
                if '"name":"' in item:
                    name = item.split('"name":"')[1].split('"')[0]
                    store = item.split('"')[0]
                    country = item.split('"country_code":"')[1].split('"')[0]
                    hours = '<MISSING>'
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    zc = item.split('"postal_code":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    typ = '<MISSING>'
                    loc = 'https://marriott.com/' + store
                    if country == 'CA' or country == 'US':
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
