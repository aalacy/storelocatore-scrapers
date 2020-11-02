import csv
import urllib.request, urllib.error, urllib.parse
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
    url = 'https://www.vw.ca/app/dccsearch/vw-ca/en/Volkswagen%20Dealer%20Search/+/49.87951181643615/-97.1759382/12/+/+/+/+'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '%5C%22,%5C%22name%5C%22:%5C%22' in line:
            items = line.split('%5C%22,%5C%22name%5C%22:%5C%22')
            for item in items:
                if '%5C%22address%5C%22:%7B%5C%22street%5C%22:%5C%22' in item:
                    website = 'vw.ca'
                    typ = '<MISSING>'
                    country = 'CA'
                    store = '<MISSING>'
                    name = item.split('%5C%22')[0].replace('%20',' ')
                    add = item.split('%5C%22address%5C%22:%7B%5C%22street%5C%22:%5C%22')[1].split('%5C')[0].replace('%20',' ')
                    city = item.split('%5C%22city%5C%22:%5C%22')[1].split('%5C')[0].replace('%20',' ')
                    state = item.split('%5C%22province%5C%22:%5C%22')[1].split('%5C')[0].replace('%20',' ')
                    zc = item.split('%5C%22postalCode%5C%22:%5C%22')[1].split('%5C')[0].replace('%20',' ')
                    phone = item.split('%5C%22phoneNumber%5C%22:%5C%22')[1].split('%5C')[0].replace('%20',' ')
                    lat = item.split('%5C%22coordinates%5C%22:%5B')[1].split(',')[0]
                    lng = item.split('%5C%22coordinates%5C%22:%5B')[1].split(',')[1].split('%')[0]
                    hours = '<MISSING>'
                    loc = '<MISSING>'
                    add = add.replace('%C3%A8','e').replace('%C3%A9','e').replace('%C3%B4','o')
                    city = city.replace('%C3%A8','e').replace('%C3%A9','e').replace('%C3%B4','o')
                    name = name.replace('%C3%A8','e').replace('%C3%A9','e').replace('%C3%B4','o')
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
