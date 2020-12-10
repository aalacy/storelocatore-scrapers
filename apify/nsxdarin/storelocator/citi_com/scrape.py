import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('citi_com')



search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
search.initialize()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json; charset=UTF-8',
           'countrycode': 'US',
           'scope': 'VISITOR',
           'sec-fetch-mode': 'cors',
           'sec-fetch-site': 'same-origin',
           'client_id': '4a51fb19-a1a7-4247-bc7e-18aa56dd1c40'
           }

MAX_RESULTS = 200
MAX_DISTANCE = 0.1

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = set()
    locations = []
    coord = search.next_coord()
    while coord:
        url = 'https://online.citi.com/gcgapi/prod/public/v1/geoLocations/places/retrieve'
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        array = []
        result_coords = []
        logger.info(('%s - %s...' % (str(x), str(y))))
        payload = '{"type":"branchesAndATMs","inputLocation":[' + str(y) + ',' + str(x) + '],"resultCount":"500","distanceUnit":"MILE","findWithinRadius":"500"}'
        payload = json.loads(payload)
        r = session.post(url, headers=headers, data=json.dumps(payload))
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"name":"' in line:
                items = line.split('"type":"Point"')
                for item in items:
                    if '{"type":"FeatureCollection"' not in item:
                        if '"additionalProperties":{"type":"branch' in item:
                            name = item.split('"name":"')[1].split('"')[0]
                            state = item.split('"state":"')[1].split('"')[0].upper()
                            add = item.split('"addressLine1":"')[1].split('"')[0].title()
                            zc = item.split('"postalCode":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0].title()
                            lng = item.split('"coordinates":[')[1].split(',')[0]
                            lat = item.split('"coordinates":[')[1].split(',')[1].split(']')[0]
                            phone = '<MISSING>'
                            try:
                                phone = item.split('"branchPhone":"')[1].split('"')[0]
                            except:
                                pass
                            country = item.split('"country":"')[1].split('"')[0]
                            typ = 'Branch'
                            website = 'citi.com'
                            store = item.split('"branchid":')[1].split(',')[0].replace('.0','')
                            hours = item.split('"hoursTeller":{')[1].split('}')[0].replace('":"','-').replace('"','').replace(',',', ')
                            lurl = '<MISSING>'
                            info = add + ';' + city + ';' + state
                            if hours == '':
                                hours = '<MISSING>'
                            array.append(info)
                            if store not in ids and 'america' in country:
                                ids.add(store)
                                country = 'US'
                                logger.info(('Pulling Store ID #%s...' % store))
                                if '-Closing' in name:
                                    name = name.split('-Closing')[0]
                                yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if len(array) <= MAX_RESULTS:
            #logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
