import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    coords = ['50.5,-4.2','51.3,-0.4','52.7,-0.26','52.9,-3.3','54.3,-3.1','56.8,-5.1','54.6,-6.7']
    for coord in coords:
        lat = coord.split(',')[0]
        lng = coord.split(',')[1]
        print(('Pulling Coordinates %s-%s...' % (lat, lng)))
        url = 'https://spatial.virtualearth.net/REST/v1/data/588775718a4b4312842f6dffb4428cff/Filialdaten-UK/Filialdaten-UK?spatialFilter=nearby(' + lat + ',' + lng + ',1000)&$filter=Adresstyp%20Eq%201&$top=1001&$format=json&$skip=0&key=Argt0lKZTug_IDWKC5e8MWmasZYNJPRs0btLw62Vnwd7VLxhOxFLW2GfwAhMK5Xg&Jsonp=displayResultStores'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"EntityID":"' in line:
                items = line.split('"EntityID":"')
                for item in items:
                    if 'CountryRegion' in item:
                        website = 'lidl.co.uk'
                        loc = '<MISSING>'
                        name = item.split('"ShownStoreName":"')[1].split('"')[0]
                        phone = '<MISSING>'
                        add = item.split('"AddressLine":"')[1].split('"')[0]
                        city = item.split('"Locality":"')[1].split('"')[0]
                        state = '<MISSING>'
                        zc = item.split('"PostalCode":"')[1].split('"')[0]
                        country = 'GB'
                        store = item.split('"')[0]
                        lat = item.split('"Latitude":')[1].split(',')[0]
                        lng = item.split('"Longitude":')[1].split(',')[0]
                        typ = '<MISSING>'
                        hours = item.split('"OpeningTimes":"')[1].split('"')[0].replace('<br>','; ')
                        if '<' in hours:
                            hours = hours.split('<')[0]
                        if store not in locs:
                            locs.append(store)
                            if hours == '':
                                hours = '<MISSING>'
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
