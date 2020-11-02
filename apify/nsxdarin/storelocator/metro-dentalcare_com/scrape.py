import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'x-requested-with': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.metro-dentalcare.com/wp-admin/admin-ajax.php'
    payload = {'action': 'prov_search',
               'data[search_type]': 'all',
               'data[lat]': '45.0',
               'data[lng]': '-93.0',
               'data[sort_field]': 'dentist_last',
               'data[sort_order]': 'ASC'
               }
    
    r = session.post(url, headers=headers, data=payload)
    website = 'metro-dentalcare.com'
    typ = 'Office'
    country = 'US'
    array = json.loads(r.content)
    for item in array['results']:
        store = item['id']
        phone = item['phone_primary']
        name = item['name']
        add = item['address1']
        add2 = item['address2']
        if add2 != '':
            add = add + ' ' + add2
        city = item['city']
        state = item['state']
        zc = item['postal_code']
        lat = item['lat']
        lng = item['lng']
        hours = 'Mon: ' + json.dumps(item['hours']['Monday'])
        hours = hours + '; ' + 'Tue: ' + json.dumps(item['hours']['Tuesday'])
        hours = hours + '; ' + 'Wed: ' + json.dumps(item['hours']['Wednesday'])
        hours = hours + '; ' + 'Thu: ' + json.dumps(item['hours']['Thursday'])
        hours = hours + '; ' + 'Fri: ' + json.dumps(item['hours']['Friday'])
        hours = hours + '; ' + 'Sat: ' + json.dumps(item['hours']['Saturday'])
        hours = hours + '; ' + 'Sun: ' + json.dumps(item['hours']['Sunday'])
        hours = hours.replace('["", ""]','Closed').replace('[','').replace('"','').replace(']','').replace(',',' -')
        phone = phone.replace('\r\n',';').replace(';;',';').replace(';;',';').replace(';;',';').replace(';;',';').replace(';;',';')
        phone = phone.replace('  PHONE','')
        if ';' in phone:
            try:
                phone = phone.split(';')[0].strip().replace(') ',')').rsplit(' ',1)[1].replace(')',') ').strip()
            except:
                phone = phone.split(';')[0].strip()
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
