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
    url = 'https://urgentandercare.com/'
    r = session.get(url, headers=headers)
    name = 'Code 3 Emergency Room'
    country = 'US'
    website = 'code3er.com'
    typ = '<MISSING>'
    store = '<MISSING>'
    for line in r.iter_lines():
        if '"address-text">' in line:
            add = line.split('"address-text">')[1].split('<')[0]
            csz = line.split('<br>')[1].split('<')[0]
            city = csz.split(',')[0]
            state = csz.split(',')[1].strip().split(' ')[0]
            zc = csz.rsplit(' ',1)[1]
        if ' alt="Phone Icon">' in line:
            phone = line.split(' alt="Phone Icon">')[1].split('<')[0]
            hours = 'Sun-Sat: 9:00am - 9:00pm'
        if 'Learn More</button>' in line:
            loc = line.split('href="')[1].split('"')[0]
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if '"latitude":"' in line2:
                    lat = line2.split('"latitude":"')[1].split('"')[0]
                    lng = line2.split('"longitude":"')[1].split('"')[0]
                    name = line2.split('"name":"')[1].split('"')[0]
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
