import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json
import  pprint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('suzukicycles_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "http://suzukicycles.com/"


    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 6
    MAX_DISTANCE = 200
    coords = search.next_zip()
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',
              'Content-type': 'application/x-www-form-urlencoded'}
    while coords:
        result_coords = []
        
        page_url ="http://suzukicycles.com/DealerSearchHandler.ashx?zip="+str(search.current_zip)+"&hasAuto=false&hasCycles=true&hasAtvs=true&hasScooters=true&hasMarine=false&maxResults=3&country=en"
        r = session.get(page_url, headers=header)
        soup = BeautifulSoup(r.text, "lxml")
        kk = soup.find_all('dealerinfo')
        for val in kk:
                # logger.info("data====",val)
                locator_domain = base_url

                location_name = val.find('name').text

                street_address = val.find('displayaddress').text

                city = val.find('city').text
                state = val.find('state').text
                zip =  val.find('zip').text

                country_code = val.find('country').text
                store_number = val.find('dealerid').text
                phone = val.find('phone').text
                phone = phone.replace("/", "-")
                location_type = ''
                latitude = val.find('esrix').text

                longitude = val.find('esriy').text
                # result_coords.append((latitude,longitude))
                hours_of_operation = '<INACCESSIBLE>'

                if street_address in addresses:
                    continue
                addresses.append(street_address)
                # page_url = base_url
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
                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                # logger.info("===", str(store))
                # return_main_object.append(store)
                yield store
        if len(kk) < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(kk) == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")

        # logger.info('hii')
        coords = search.next_zip()
        # break

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
