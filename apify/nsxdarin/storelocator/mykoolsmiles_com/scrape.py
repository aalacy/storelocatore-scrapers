import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mykoolsmiles_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-requested-with': 'XMLHttpRequest',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for code in sgzip.for_radius(50):
        logger.info(('Pulling Zip Code %s...' % code))
        url = 'https://www.mykoolsmiles.com/api/locations/find_nearest'
        payload = {'zip': code,
                   'about_myself': 'other',
                   'page': 'https://www.mykoolsmiles.com/'
                   }
        r = session.post(url, headers=headers, data=payload)
        array = json.loads(r.content)
        for item in array:
            website = 'mykoolsmiles.com'
            typ = 'Office'
            name = item['FacilityName']
            add = item['Address1']
            city = item['City']
            state = item['State']
            zc = item['ZIP']
            phone = item['OfficePhone']
            country = 'US'
            store = item['location_id']
            hours = 'Mon: ' + item['Mon_Hours']
            hours = hours + '; Tue: ' + item['Tue_Hours']
            hours = hours + '; Wed: ' + item['Wed_Hours']
            hours = hours + '; Thu: ' + item['Thu_Hours']
            hours = hours + '; Fri: ' + item['Fri_Hours']
            hours = hours + '; Sat: ' + item['Sat_Hours']
            if 'Sun_Hours":""' not in item:
                hours = hours + '; Sun: ' + item['Sun_Hours']
            else:
                hours = hours + '; Sun: Closed'
            hours = hours.replace('; Sat: ;','; Sat: Closed;')
            lat = item['latitude']
            lng = item['longitude']
            if store not in ids:
                ids.append(store)
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
