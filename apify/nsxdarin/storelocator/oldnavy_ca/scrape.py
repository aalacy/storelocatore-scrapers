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
    url = 'https://oldnavy.gapcanada.ca/customerService/info.do?cid=57308&mlink=5151,8551677,7'
    r = session.get(url, headers=headers)
    Found = False
    website = 'oldnavy.ca'
    typ = '<MISSING>'
    hours = '<MISSING>'
    for line in r.iter_lines():
        if ' var caStores=[' in line:
            Found = True
        if Found and '</script>' in line:
            Found = False
        if Found and ", '" in line and "store locator ID" not in line:
            name = line.split("'")[1]
            add = line.split("'")[3]
            city = line.split("'")[5]
            state = line.split("'")[7]
            country = 'CA'
            zc = line.split("'")[9]
            phone = line.split("'")[11]
            lat = line.split("',")[6].split(']')[0].split(',')[8].strip()
            lng = line.split("',")[6].split(']')[0].split(',')[9].strip()
            loc = '<MISSING>'
            store = '<MISSING>'
            if zc == '':
                zc = '<MISSING>'
            if phone == '':
                phone = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
