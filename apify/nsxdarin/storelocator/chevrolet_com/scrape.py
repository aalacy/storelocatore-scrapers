import csv
import sgzip
from sgrequests import SgRequests

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'authority': 'www.chevrolet.ca',
           'accept': 'application/json, text/plain, */*',
           'clientapplicationid': 'OCNATIVEAPP',
           'loginin': 'mytest016@outlook.com',
           'locale': 'en_US'
           }

MAX_RESULTS = 50
MAX_DISTANCE = 10

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
        url = 'https://www.chevrolet.com/OCRestServices/dealer/latlong/v1/chevrolet/' + str(llat) + '/' + str(llng) + '/?distance=500&maxResults=50'
        r = session.get(url, headers=headers)
        result_coords = []
        array = []
        website = 'chevrolet.com'
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '{"id":' in line:
                items = line.split('{"id":')
                for item in items:
                    if '"dealerName":"' in item:
                        try:
                            name = item.split('"dealerName":"')[1].split('"')[0]
                            store = item.split(',')[0]
                            typ = '<MISSING>'
                            try:
                                loc = item.split('"dealerUrl":"')[1].split('"')[0]
                            except:
                                loc = '<MISSING>'
                            phone = item.split('"phone1":"')[1].split('"')[0]
                            add = item.split('{"addressLine1":"')[1].split('"')[0]
                            city = item.split('"cityName":"')[1].split('"')[0]
                            state = item.split('"countrySubdivisionCode":"')[1].split('"')[0]
                            zc = item.split(',"postalCode":"')[1].split('"')[0]
                            country = 'US'
                            lat = item.split('"latitude":')[1].split(',')[0]
                            hours = ''
                            lng = item.split('"longitude":')[1].split('}')[0]
                            try:
                                days = item.split('"generalOpeningHour":[{')[1].split('}],"serviceOpeningHour":')[0].split('"openFrom":"')
                                for day in days:
                                    if '"dayOfWeek":' in day:
                                        dname = day.split('"dayOfWeek":[')[1].split(']')[0]
                                        dname = dname.replace('1','Mon').replace('2','Tue').replace('3','Wed').replace('4','Thu').replace('5','Fri').replace('6','Sat').replace('7','Sun')
                                        hrs = dname + ': ' + day.split('"')[0] + '-' + day.split(',"openTo":"')[1].split('"')[0]
                                        if hours == '':
                                            hours = hrs
                                        else:
                                            hours = hours + '; ' + hrs
                            except:
                                hours = '<MISSING>'
                            if 'Mon' in hours and 'Sun' not in hours:
                                hours = hours + '; Sun: Closed'
                            array.append(store)
                            zc = zc[:5]
                            if store not in sids:
                                sids.append(store)
                                #print(store)
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
