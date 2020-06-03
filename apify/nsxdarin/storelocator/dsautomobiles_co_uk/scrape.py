import csv
import urllib2
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
    url = 'https://www.dsautomobiles.co.uk/_/Layout_DSPP_DealerLocator/getStoreList?lat=51.51&long=-0.13&page=15041&version=58&order=2&area=50000&ztid=&attribut=&brandactivity=DS'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '{"id":"' in line:
            items = line.split('{"id":"')
            for item in items:
                if ',"name":"' in item:
                    name = item.split(',"name":"')[1].split('"')[0]
                    website = 'dsautomobiles.co.uk'
                    typ = '<MISSING>'
                    country = 'GB'
                    hours = '<MISSING>'
                    loc = '<MISSING>'
                    addinfo = item.split('"address":"')[1].split('"')[0]
                    add = addinfo.split('<br')[0]
                    city = addinfo.rsplit('&nbsp;',1)[1]
                    state = '<MISSING>'
                    zc = addinfo.split('<br \\/>')[1].split('&')[0]
                    phone = item.split(',"phone":"')[1].split('"')[0]
                    store = item.split('"')[0]
                    lat = item.split('"lat":')[1].split(',')[0]
                    lng = item.split('"lng":')[1].split(',')[0]
                    add = add.replace('&nbsp;-','').replace('&nbsp;',' ').replace('\\/','/')
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
