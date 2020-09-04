import csv
import sgzip
from sgrequests import SgRequests

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'authority': 'www.t-mobile.com',
           'accept': 'application/json, text/plain, */*',
           'clientapplicationid': 'OCNATIVEAPP',
           'loginin': 'mytest016@outlook.com',
           'locale': 'en_US'
           }

MAX_RESULTS = 50
MAX_DISTANCE = 25

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    sids = []
    ids = []
    locations = []
    coord = search.next_coord()
    while coord:
        llat = coord[0]
        llng = coord[1]
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        #print('%s-%s...' % (llat, llng))
        url = 'https://onmyj41p3c.execute-api.us-west-2.amazonaws.com/prod/v2.1/getStoresByCoordinates?latitude=' + str(llat) + '&longitude=' + str(llng) + '&count=50&radius=100&ignoreLoadin{%22id%22:%22gBar=false'
        r = session.get(url, headers=headers)
        result_coords = []
        array = []
        website = 'sprint.com'
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"id":"' in line:
                items = line.split('{"id":"')
                for item in items:
                    if '"type":"' in item:
                        try:
                            name = item.split('"name":"')[1].split('"')[0]
                            store = item.split('"')[0]
                            typ = item.split('"type":"')[1].split('"')[0]
                            loc = item.split('"url":"')[1].split('"')[0]
                            phone = item.split('"telephone":"')[1].split('"')[0]
                            add = item.split('"streetAddress":"')[1].split('"')[0]
                            city = item.split('"addressLocality":"')[1].split('"')[0]
                            state = item.split('"addressRegion":"')[1].split('"')[0]
                            zc = item.split(',"postalCode":"')[1].split('"')[0]
                            country = 'US'
                            lat = item.split('"latitude":')[1].split(',')[0]
                            hours = ''
                            lng = item.split('"longitude":')[1].split(',')[0]
                            days = item.split('"standardHours":[')[1].split(']')[0].split('"day":"')
                            for day in days:
                                if '"opens":"' in day:
                                    hrs = day.split('"')[0] + ': ' + day.split('"opens":"')[1].split('"')[0] + '-' + day.split('"closes":"')[1].split('"')[0]
                                    if hours == '':
                                        hours = hrs
                                    else:
                                        hours = hours + '; ' + hrs
                            array.append(store)
                            if hours == '':
                                hours = '<MISSING>'
                            if store not in sids:
                                sids.append(store)
                                #print(store)
                                if '"hasSprintStack":true' in item and '"storeDefinition":"(TPR)Third Party Retail"' in item and '"hasTmobileStack":false' in item:
                                    typ = 'Sprint Store'
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                        except:
                            pass
        if len(array) <= MAX_RESULTS:
                    print("max distance update")
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
