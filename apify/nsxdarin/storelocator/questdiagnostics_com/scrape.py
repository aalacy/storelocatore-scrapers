import csv
import urllib2
from sgrequests import SgRequests
import json
from sgzip import sgzip

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'Content-Type': 'application/json',
           'Cookie': 'demyq=c082a85d-14e0-434b-8b93-016cade2fa31'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    url_home = 'https://appointment.questdiagnostics.com/patient/findlocation'
    url = 'https://appointment.questdiagnostics.com/as-service/services/getQuestLocations'
    for coord in sgzip.coords_for_radius(100):
        x = float(coord[0])
        y = float(coord[1])
        x = str(round(x, 2))
        y = str(round(y, 2))
        print('%s - %s...' % (str(x), str(y)))
        payload = '{"miles":100,"address":{},"latitude":' + str(x) + ',"longitude":' + str(y) + ',"serviceType":["all"],"maxReturn":100,"onlyScheduled":"false","accessType":[],"questDirect":false}'
        payload = json.loads(payload)
        r = session.post(url, data=json.dumps(payload), headers=headers)
        for line in r.iter_lines():
            if '"name":"' in line:
                items = line.split('"name":"')
                for item in items:
                    if '"address":"' in item:
                        name = item.split('"')[0]
                        add = item.split('"address":"')[1].split('"')[0] + ' ' + item.split('"address2":"')[1].split('"')[0]
                        add = add.strip()
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"zip":"')[1].split('"')[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        store = item.split('siteCode":"')[1].split('"')[0]
                        website = 'questdiagnostics.com'
                        hours = item.split('"hoursOfOperations":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(',')[0]
                        lng = item.split('"longitude":')[1].split(',')[0]
                        typ = item.split('"locationType":"')[1].split('"')[0].strip()
                        country = 'US'
                        lurl = '<MISSING>'
                        if typ == '':
                            typ = '<MISSING>'
                        if phone == '':
                            phone = '<MISSING>'
                        if hours == '':
                            hours = '<MISSING>'
                        if store not in ids:
                            ids.append(store)
                            print('Pulling Location %s...' % store)
                            yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
