import csv
import urllib2
from sgrequests import SgRequests
import sgzip

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

MAX_RESULTS = 250
MAX_DISTANCE = 5

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = set()
    locations = []
    alllocs = []
    coord = search.next_coord()
    while coord:
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        website = 'verizonwireless.com'
        #print('%s, %s...' % (x, y))
        url = 'https://www.verizonwireless.com/stores/storesearchresults/?lat=' + str(x) + '&long=' + str(y)
        r = session.get(url, headers=headers)
        result_coords = []
        purl = '<MISSING>'
        array = []
        for line in r.iter_lines():
            if 'var searchJSON' in line:
                items = line.split('"storeName":"')
                for item in items:
                    if '"address":"' in item:
                        purl = 'https://www.verizonwireless.com' + item.split('"storeUrl":"')[1].split('"')[0]
                        typ = item.split('"typeOfStore":["')[1].split('"')[0]
                        name = item.split('"')[0]
                        add = item.split('"address":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"stateAbbr":"')[1].split('"')[0]
                        country = 'US'
                        zc = item.split('"zip":"')[1].split('"')[0]
                        store = item.split('"storeNumber":"')[1].split('"')[0]
                        lat = item.split('lat":"')[1].split('"')[0]
                        lng = item.split('lng":"')[1].split('"')[0]
                        try:
                            phone = item.split('"phone":"')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                        try:
                            hours = item.split('"openingHours":{')[1].split('}')[0].replace('":"',': ').replace('","','; ').replace('"','')
                        except:
                            hours = ''
                        info = add + ';' + city + ';' + state
                        if hours == '':
                            hours = '<MISSING>'
                        ids.add(info)
                        array.append(info)
                        if purl not in alllocs:
                            alllocs.append(purl)
                            yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if len(array) <= MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
##        elif len(array) == MAX_RESULTS:
##            print("max count update")
##            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
