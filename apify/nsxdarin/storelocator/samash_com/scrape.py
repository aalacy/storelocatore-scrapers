import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('samash_com')



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
    url = 'https://hosted.where2getit.com/samashmusic/rest/getlist?lang=en_US'
    payload = {"request":{"appkey":"F1BBEE32-0D3E-11DF-AB7B-8CB43B999D57","formdata":{"objectname":"Account::State","where":{"country":"US"}}}}
    r = session.post(url, data=json.dumps(payload), headers=headers)
    states = []
    array = json.loads(r.content)
    for item in array['response']['collection']:
        states.append(item['name'])
    for state in states:
        logger.info(('Pulling State %s...' % state))
        url = 'https://hosted.where2getit.com/samashmusic/rest/getlist?lang=en_US'
        payload = {"request":{"appkey":"F1BBEE32-0D3E-11DF-AB7B-8CB43B999D57","formdata":{"order":"city","-softmatch":"1","objectname":"Locator::Store","where":{"clientkey":{"eq":""},"state":{"eq":state},"name":{"ilike":""}}}}}
        r = session.post(url, data=json.dumps(payload), headers=headers)
        results = json.loads(r.content)
        for loc in results['response']['collection']:
            website = 'samash.com'
            name = loc['name']
            add = loc['address1']
            city = loc['city']
            state = loc['state']
            zc = loc['postalcode']
            phone = loc['phone']
            hours = 'Mon-Thu: ' + loc['hoursmonthur']
            hours = hours + '; ' + 'Fri: ' + loc['hoursfri']
            hours = hours + '; ' + 'Sat: ' + loc['hourssat']
            hours = hours + '; ' + 'Sun: ' + loc['hourssunday']
            country = loc['country']
            typ = 'Store'
            store = loc['clientkey']
            lat = loc['latitude']
            lng = loc['longitude']
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
