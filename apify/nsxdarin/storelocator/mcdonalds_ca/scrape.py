import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=43.6424036&longitude=-79.3859716&radius=5000&maxResults=50000&country=ca&language=en-ca&showClosed=&hours24Text=Open%2024%20hr'
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array['features']:
        store = item['properties']['identifiers']['storeIdentifier'][0]['identifierValue']
        add = item['properties']['addressLine1']
        add = add.strip().replace('"',"'")
        city = item['properties']['addressLine3']
        state = '<MISSING>'
        country = 'CA'
        zc = item['properties']['postcode']
        try:
            phone = item['properties']['telephone']
        except:
            phone = '<MISSING>'
        name = "McDonald's # " + store
        website = 'mcdonalds.com'
        typ = 'Restaurant'
        lat = item['geometry']['coordinates'][1]
        lng = item['geometry']['coordinates'][0]
        try:
            hours = 'Mon: ' + item['properties']['restauranthours']['hoursMonday']
            hours = hours + '; Tue: ' + item['properties']['restauranthours']['hoursTuesday']
            hours = hours + '; Wed: ' + item['properties']['restauranthours']['hoursWednesday']
            hours = hours + '; Thu: ' + item['properties']['restauranthours']['hoursThursday']
            hours = hours + '; Fri: ' + item['properties']['restauranthours']['hoursFriday']
            hours = hours + '; Sat: ' + item['properties']['restauranthours']['hoursSaturday']
            hours = hours + '; Sun: ' + item['properties']['restauranthours']['hoursSunday']
        except:
            hours = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
