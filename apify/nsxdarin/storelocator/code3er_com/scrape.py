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
    url = 'https://urgentandercare.com/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    name = 'Code 3 Emergency Room'
    country = 'US'
    website = 'code3er.com'
    typ = '<MISSING>'
    store = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    for line in r.iter_lines(decode_unicode=True):
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
            if r2.encoding is None: r2.encoding = 'utf-8'
            for line2 in r2.iter_lines(decode_unicode=True):
                if '"latitude":"' in line2:
                    lat = line2.split('"latitude":"')[1].split('"')[0]
                    lng = line2.split('"longitude":"')[1].split('"')[0]
                    name = line2.split('"name":"')[1].split('"')[0]
            if 'carrollton.urgentandercare.com' in loc:
                lat = '33.0266096'
                lng = '-96.8840568'
            if 'denton' in loc:
                lat = '33.1762313'
                lng = '-97.1143493'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
