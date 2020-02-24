import csv
import urllib2
from sgrequests import SgRequests
import json
import sgzip

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'Content-Type': 'application/json',
           'Cookie': '_hjid=da1124c4-fe5e-4ef0-b222-e2d874de20dc; f5avrbbbbbbbbbbbbbbbb=CDEANDNOHPBCKCHOLJDPLMEBFBHEPMHMIKPKBOIBIPECHGAMLPHEEOJHOLBLMNAOHOODIBEGLEKNOIEPLGGAIMLGCNJKDLDOPJMHFEBNKFAOCBLDMMFFBNAEHMFMJKFI; demyq=dd4ad953-9d7d-4c21-bc20-9b72225e9c41; TS01977cc6=01aae08daf7f3ab9a6ce8ff9f5601e735c91b7ed705b8ca652e056035a34a693a0c56a76b4267010cf45d00e75adfb72214337cea8077648cdd54e1e542638ca131cacd262; _ga=GA1.2.486596660.1578947702; _gid=GA1.2.911363656.1578947702; _dc_gtm_UA-100362401-1=1; _dc_gtm_UA-921392-21=1; _dc_gtm_UA-921392-12=1; CSRF-TOKEN=6fd16efa8e63b7fbca9b83d37e4809d24b',
           'X-CSRF-TOKEN': '6cf6d70b6e71c6ef264cb0c5e303afdcb6'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    url = 'https://appointment.questdiagnostics.com/as-service/services/getQuestLocations'
    for coord in sgzip.coords_for_radius(100):
        x = float(coord[0])
        y = float(coord[1])
        x = str(round(x, 2))
        y = str(round(y, 2))
        print('%s - %s...' % (str(x), str(y)))
        payload = '{"miles":100,"address":{},"latitude":' + str(x) + ',"longitude":' + str(y) + ',"serviceType":["all"],"maxReturn":100,"onlyScheduled":"false","accessType":[],"questDirect":false}'
        payload = json.loads(payload)
        r = session.post(url, headers=headers, data=json.dumps(payload))
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
