import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://locator.nbc.ca/?branch&atm'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines(decode_unicode = True):
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if 'setArrGeoCoord' not in item:
                    store = item.split('"corporateId":"')[1].split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0].replace('\\/','/')
                    website = 'nbc.ca'
                    typ = item.split('categoryIndex":"')[1].split('"')[0]
                    try:
                        phone = item.split('"phone":"')[1].split('"')[0]
                    except:
                        phone = '<MISSING>'
                    add = item.split('"address":"')[1].split('"')[0].replace('\\/','/')
                    state = item.split('"region":"')[1].split('"')[0].replace('\\/','/')
                    city = item.split('"locality":"')[1].split('"')[0].replace('\\/','/')
                    zc = item.split(',"postcode":"')[1].split('"')[0]
                    country = 'CA'
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lon":"')[1].split('"')[0]
                    hours = item.split('"storeHours":"')[1].split('","lat":"')[0]
                    hours = hours.replace('<\\/td><\\/tr><tr><td>','; ')
                    hours = hours.replace('<\\/td><td class=\\"table_hours_right\\">',' - ')
                    hours = hours.replace('<table><tr><td>','')
                    hours = hours.replace('<\\/b><\\/b><\\/td><\\/tr><tr><td>','; ')
                    hours = hours.replace('<\\/tr>','').replace('<\\/td>','').replace('<\\/table>','')
                    hours = hours.replace('<b>','').replace('<\\/b>','').replace('24\\/7','')
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
