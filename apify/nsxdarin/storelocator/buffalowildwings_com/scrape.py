import csv
import urllib2
import requests
import json
from sgzip import sgzip

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'X_CLIENT_ID': '4171883342bf4b88aa4b88ec77f5702b',
           'X_CLIENT_SECRET': '786c1B856fA542C4b383F3E8Cdd36f3f'
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
        print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://api.buffalowildwings.com/BWWService.svc/GetRestaurntDetailsByltdLng?fLatitude=' + x + '&fLongitude=' + y + '&radius=500&iVendorID=50'
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        for item in array:
            try:
                try:
                    state = item['State']
                except:
                    state = '<MISSING>'
                name = item['LocationName']
                typ = item['ConceptName']
                store = item['RestaurantNumber']
                lat = item['Latitude']
                lng = item['Longitude']
                website = 'buffalowildwings.com'
                zc = item['PostalCode']
                add = item['AddressLine1']
                try:
                    add = add + ' ' + item['AddressLine2']
                except:
                    pass
                city = item['City']
                country = 'US'
                phone = item['RestaurantPhoneNumber']
                if '-' not in phone:
                    phone = '<MISSING>'
                try:
                    hours = 'Mon: ' + item['HourOfOperationMonOpen'] + '-' + item['HourOfOperationMonclose']
                    hours = hours + '; Tue: ' + item['HourOfOperationTueOpen'] + '-' + item['HourOfOperationTueClose']
                    hours = hours + '; Wed: ' + item['HourOfOperationWedOpen'] + '-' + item['HourOfOperationWedClose']
                    hours = hours + '; Thu: ' + item['HourOfOperationThuOpen'] + '-' + item['HourOfOperationThuClose']
                    hours = hours + '; Fri: ' + item['HourOfOperationFriOpen'] + '-' + item['HourOfOperationFriClose']
                    hours = hours + '; Sat: ' + item['HourOfOperationSatOpen'] + '-' + item['HourOfOperationSatClose']
                    hours = hours + '; Sun: ' + item['HourOfOperationSunOpen'] + '-' + item['HourOfOperationSunClose']
                except:
                    hours = '<MISSING>'
                if add != '' and store not in ids and len(state) == 2:
                    ids.append(store)
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                pass

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
