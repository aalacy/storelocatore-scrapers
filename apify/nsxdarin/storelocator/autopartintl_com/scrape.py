import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('autopartintl_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'x-requsted-with': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        logger.info(('Pulling Lat-Long %s,%s...' % (str(x), str(y))))
        url = 'https://www.autopartintl.com/autopart/wp-admin/admin-ajax.php'
        payload = {'address': '',
                   'formdata': 'addressInput=',
                   'lat': x,
                   'lng': y,
                   'name': '',
                   'options[distance_unit]': 'miles',
                   'options[dropdown_style]': 'none',
                   'options[ignore_radius]': '0',
                   'options[immediately_show_locations]': '0',
                   'options[initial_radius]': '10000',
                   'options[label_directions]': 'Directions',
                   'options[label_email]': 'Email',
                   'options[label_fax]': 'Fax',
                   'options[label_phone]': 'Phone',
                   'options[label_website]': 'Website',
                   'options[loading_indicator]': '',
                   'options[map_domain]': 'maps.google.com',
                   'options[map_region]': 'us',
                   'options[no_autozoom]': '0',
                   'options[use_sensor]': '0',
                   'radius': '500',
                   'tags': '',
                   'action': 'csl_ajax_search'
                   }
                   
        r = session.post(url, headers=headers, data=payload)
        array = json.loads(r.content)
        for item in array['response']:
            website = 'autopartintl.com'
            typ = 'Store'
            name = item['name']
            add = item['address'] + ' ' + item['address2']
            city = item['city']
            state = item['state']
            zc = item['zip']
            phone = item['phone']
            country = 'US'
            store = item['id']
            hours = item['hours'].replace('\r\n',' ')
            lat = item['lat']
            lng = item['lng']
            if store not in ids:
                ids.append(store)
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
