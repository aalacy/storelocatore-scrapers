import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'x-requested-with': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.southernstates.com/api/es/search?pretty'
    payload = {"sort":{"_geo_distance":
                       {"store.latlong":
                        {"lat":39.0025,"lon":-76.1424},
                        "order":"asc","unit":"km"}},
               "query":{"term":{"store.webPublish":"1"}},
               "size":2000,"filter":
               {"geo_distance":{"distance":"1000miles",
                                "store.latlong":
                                {"lat":39.0025,"lon":-76.1424}}}}
    r = session.post(url, headers=headers, data=json.dumps(payload))
    array = json.loads(r.content)
    for item in array['contentlets']:
        website = 'southernstates.com'
        store = item['storeNumber']
        phone = item['phone']
        city = item['city']
        state = item['stateAbbr']
        add = item['address1'] + ' ' + item['address2']
        add = add.strip()
        name = item['storeName']
        lat = item['latlong'].split(',')[0]
        lng = item['latlong'].split(',')[1]
        country = 'US'
        typ = 'Store'
        zc = item['zipcode']
        hours = 'Mon: ' + item['storeOpenMonday'].split(' ')[1].rsplit(':',1)[0] + '-' + item['storeCloseMonday'].split(' ')[1].rsplit(':',1)[0]
        hours = hours + '; ' + 'Tue: ' + item['storeOpenTuesday'].split(' ')[1].rsplit(':',1)[0] + '-' + item['storeCloseTuesday'].split(' ')[1].rsplit(':',1)[0]
        hours = hours + '; ' + 'Wed: ' + item['storeOpenWednesday'].split(' ')[1].rsplit(':',1)[0] + '-' + item['storeCloseWednesday'].split(' ')[1].rsplit(':',1)[0]
        hours = hours + '; ' + 'Thu: ' + item['storeOpenThursday'].split(' ')[1].rsplit(':',1)[0] + '-' + item['storeCloseThursday'].split(' ')[1].rsplit(':',1)[0]
        hours = hours + '; ' + 'Fri: ' + item['storeOpenFriday'].split(' ')[1].rsplit(':',1)[0] + '-' + item['storeCloseFriday'].split(' ')[1].rsplit(':',1)[0]
        hours = hours + '; ' + 'Sat: ' + item['storeOpenSaturday'].split(' ')[1].rsplit(':',1)[0] + '-' + item['storeCloseSaturday'].split(' ')[1].rsplit(':',1)[0]
        hours = hours + '; ' + 'Sun: ' + item['storeOpenSunday'].split(' ')[1].rsplit(':',1)[0] + '-' + item['storeCloseSunday'].split(' ')[1].rsplit(':',1)[0]
        if phone == '':
            phone = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
