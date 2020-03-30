import csv
import urllib2
from sgrequests import SgRequests
import sgzip
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
    ids = []
    for coord in sgzip.coords_for_radius(200):
        x = coord[0]
        y = coord[1]
        print('Pulling Zip Lat-Lng %s-%s...' % (x, y))
        payload = {"request":{"appkey":"E76CAAF4-9877-11E1-9438-A503DEB2B31E","formdata":{"geoip":"false","dataview":"store_default","limit":5000,
                                                                                          "reviews":{"bd":1},"order":"rank::numeric, _DISTANCE",
                                                                                          "geolocs":{"geoloc":[{"addressline":"","country":"US","latitude":x,"longitude":y,"state":"","province":"",
                                                                                                                "city":"","address1":"","postalcode":""}]},
                                                                                          "searchradius":"5000","where":{"or":{"icon":{"in":""}}},"false":"0"}}}
        url = 'https://hosted.where2getit.com/uggaustralia/rest/locatorsearch?like=0.5506876374626519&lang=en_EN'
        r = session.post(url, headers=headers, data=json.dumps(payload))
        array = json.loads(r.content)['response']
        for item in array[0]['collection']:
            country = item['country']
            if country == 'US' or country == 'CA':
                lat = item['latitude']
                lng = item['longitude']
                zc = item['postalcode']
                name = item['name'].encode('utf-8')
                if item['address2']:
                    add = item['address1'].encode('utf-8') + ' ' + item['address2'].encode('utf-8')
                else:                    
                    add = item['address1'].encode('utf-8')
                try:
                    add = add.strip().replace('"',"'")
                except:
                    add = ''
                state = item['state']
                if item['city'] is not None:
                    city = item['city'].encode('utf-8')
                website = 'ugg.com'
                phone = item['phone']
                if item['province'] is not None:
                    try:
                        state = item['province']
                    except:
                        state = state
                hours = '<MISSING>'
                typ = item['storetype']
                if typ == '':
                    typ = 'Store'
                store = item['clientkey'].encode('utf-8')
                if item['mon_hours']:
                    hours = 'Mon: ' + item['mon_hours']
                    hours = hours + '; Tue: ' + item['tue_hours']
                    hours = hours + '; Wed: ' + item['wed_hours']
                    hours = hours + '; Thu: ' + item['thu_hours']
                    hours = hours + '; Fri: ' + item['fri_hours']
                    hours = hours + '; Sat: ' + item['sat_hours']
                    hours = hours + '; Sun: ' + item['sun_hours']
                if 'null' in hours:
                    hours = '<MISSING>'
                if phone is None or phone == '':
                    phone = '<MISSING>'
                if zc is None or zc == '':
                    zc = '<MISSING>'
                if city is None or city == '':
                    city = '<MISSING>'
                if state is None or state == '':
                    state = '<MISSING>'
                if typ == '':
                    typ = '<MISSING>'
                if store not in ids and add != '':
                    ids.append(store)
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
