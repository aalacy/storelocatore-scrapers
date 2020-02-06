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
    url = 'https://locationservices.wendys.com/LocationServices/rest/nearbyLocations?&lang=en&cntry=US&sourceCode=ORDER.WENDYS&version=5.33.3&address=55408&limit=10000&filterSearch=true&radius=10000'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<address1>' in line:
            items = line.split('<address1>')
            for item in items:
                if '<address2>' in item:
                    website = 'wendys.com'
                    add = item.split('<')[0]
                    add = add + ' ' + item.split('<address2>')[1].split('<')[0]
                    add = add.strip()
                    name = item.split('<name>')[1].split('<')[0]
                    city = item.split('<city>')[1].split('<')[0]
                    state = item.split('<state>')[1].split('<')[0]
                    country = item.split('<country>')[1].split('<')[0]
                    lat = item.split('<lat>')[1].split('<')[0]
                    lng = item.split('<lng>')[1].split('<')[0]
                    phone = item.split('<phone>')[1].split('<')[0]
                    days = item.split('<daysOfWeek>')
                    typ = 'Restaurant'
                    for day in days:
                        if '1</day>' in day:
                            hours = 'Sun: ' + day.split('<openTime>')[1].split(':00</open')[0] + '-' + day.split('<closeTime>')[1].split(':00</close')[0]
                        if '2</day>' in day:
                            hours = hours + '; Mon: ' + day.split('<openTime>')[1].split(':00</open')[0] + '-' + day.split('<closeTime>')[1].split(':00</close')[0]
                        if '3</day>' in day:
                            hours = hours + '; Tue: ' + day.split('<openTime>')[1].split(':00</open')[0] + '-' + day.split('<closeTime>')[1].split(':00</close')[0]
                        if '4</day>' in day:
                            hours = hours + '; Wed: ' + day.split('<openTime>')[1].split(':00</open')[0] + '-' + day.split('<closeTime>')[1].split(':00</close')[0]
                        if '5</day>' in day:
                            hours = hours + '; Thu: ' + day.split('<openTime>')[1].split(':00</open')[0] + '-' + day.split('<closeTime>')[1].split(':00</close')[0]
                        if '6</day>' in day:
                            hours = hours + '; Fri: ' + day.split('<openTime>')[1].split(':00</open')[0] + '-' + day.split('<closeTime>')[1].split(':00</close')[0]
                        if '7</day>' in day:
                            hours = hours + '; Sat: ' + day.split('<openTime>')[1].split(':00</open')[0] + '-' + day.split('<closeTime>')[1].split(':00</close')[0]
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
