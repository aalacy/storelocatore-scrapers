import csv
import sys

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dunkindonuts_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    base_url = "https://www.dunkindonuts.com/"
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["US"])
    postcode = search.next_zip()

    MAX_RESULTS = 30
    # MAX_COUNT = 32
    MAX_DISTANCE = 25
    current_results_len =0
    addresses = []

    while postcode:
        result_coords = []
        # z = str(search.current_zip)
        # try:
        r = session.get("https://www.mapquestapi.com/search/v2/radius?callback=jQuery22408729727990432037_1568814338463&key=Gmjtd%7Clu6t2luan5%252C72%253Do5-larsq&origin=" + str(postcode) + "&units=m&maxMatches=30&radius=25&hostedData=mqap.33454_DunkinDonuts&ambiguities=ignore&_=1568814338464")
            
        # except:
        #     pass
        
        soup = BeautifulSoup(r.text, "lxml")

        ck = soup.text.split('jQuery22408729727990432037_1568814338463(')[1].split(');')[0]
        data_json = json.loads(ck)
        # logger.info(data_json)
        if "searchResults" in data_json:
            current_results_len = len(data_json['searchResults'])
            for x in data_json['searchResults']:
                vj = x['fields']

                locator_domain = base_url

                location_name = 'Dunkin Donuts'
                street_address = vj['address'].strip() + vj['address2']

                city = vj['city'].strip()
                state = vj['state'].strip()
                zip = vj['postal'].strip()

                store_number = vj['recordid']
                country_code = vj['country'].strip()
                if vj['phonenumber'] == '--':
                    phone = ''
                else:
                    phone = vj['phonenumber'].strip()
                location_type = '<MISSING>'
                latitude = vj['lat']
                longitude = vj['lng']

                if street_address in addresses:
                    continue
                addresses.append(street_address)

                hours_of_operation = ' mon ' + vj['mon_hours'] + '  tue ' + vj['tue_hours'] + ' wed ' + vj['wed_hours'] + \
                    ' thu ' + vj['thu_hours'] + ' fri ' + vj['fri_hours'] + \
                    ' sat ' + vj['sat_hours'] + ' sun ' + vj['sun_hours']
                page_url = "https://www.dunkindonuts.com/en/locations?location=" + \
                    str(postcode)

                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zip if zip else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                result_coords.append((latitude, longitude))
                store.append(
                    hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else "<MISSING>")

                # logger.info("data == " + str(store))
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store
            


        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")

        postcode = search.next_zip()
       
    # return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
