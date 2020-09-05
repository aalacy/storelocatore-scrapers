import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://sabasofchandler.com'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    website = 'sabasofchandler.com'
    name = "Saba Western Wear"
    store = '<MISSING>'
    country = 'US'
    add = ''
    city = ''
    state = ''
    zc = ''
    hours = ''
    typ = 'Store'
    lat = ''
    lng = ''
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if 'places":[{"address":"' in line:
            add = line.split('places":[{"address":"')[1].split(',')[0].strip()
            city = line.split('places":[{"address":"')[1].split(',')[1].strip()
            state = line.split('places":[{"address":"')[1].split(',')[2].strip().split(' ')[0]
            zc = line.split('places":[{"address":"')[1].split(',')[2].strip().split(' ')[1].split('"')[0]
            lat = line.split('"latitude":"')[1].split('"')[0]
            lng = line.split('"longitude":"')[1].split('"')[0]
        if 'Shop Open:</h4>' in line:
            next(lines)
            next(lines)
            hours = next(lines).split('">')[1].split('<')[0]
            hours = hours + '; ' + next(lines).split('<')[0]
        if 'href="tel:' in line:
            phone = line.split('href="tel:')[1].split('"')[0]
    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
