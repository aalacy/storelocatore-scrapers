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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=40.0&longitude=-95.0&radius=10000&maxResults=30000&country=us&language=en-us&showClosed=&hours24Text=Open%2024%20hr'
    r = session.get(url, headers=headers)
    array = json.loads(r.content)

    country = 'US'
    website = 'mcdonalds.com'
    typ = 'Restaurant'
    page_url = 'https://www.mcdonalds.com/ca/en-ca/restaurant-locator.html'

    for item in array['features']:
        store = item['properties']['identifierValue']
        add = item['properties']['addressLine1']
        add = add.strip()
        city = item['properties']['addressLine3']
        state = item['properties']['subDivision']
        zc = item['properties']['postcode']
        phone = item['properties']['telephone']
        name = "McDonald's # " + store
        lat = item['geometry']['coordinates'][0]
        lng = item['geometry']['coordinates'][1]
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
        yield [website, page_url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

if __name__ == "__main__":
    scrape()
