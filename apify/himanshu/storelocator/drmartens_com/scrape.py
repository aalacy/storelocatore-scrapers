import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('drmartens_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 30
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    base_url = "https://www.drmartens.com/"
    while zip_code:
        result_coords = []
        # logger.info("zips === " + str(zip_code))
        try:
            r = session.get("https://www.drmartens.com/us/en/store-finder?q="+str(zip_code), headers=headers)
        except:
            pass
            raise Exception(r)
        if '<html lang="en">' not in r.text:       
            location_url = r.json()
            current_results_len = len(location_url['data'])
            for address_list in location_url['data']:
                location_name = address_list['displayName']
                latitude = address_list['latitude']
                longitude = address_list['longitude']
                phone = address_list['phone']
                street_address = address_list['line1']+" "+address_list['line2']

                if "," in address_list['town']:
                    city = address_list['town'].split(',')[0]
                    state = address_list['town'].split(',')[1].strip()

                elif len(address_list['town']) == 2:
                    city = address_list['line2']
                    state = address_list['town']

                elif " " in address_list['town']:
                    city = address_list['town'].split(' ')[0]
                    state = address_list['town'].split(' ')[1]
                else:
                    city = address_list['town']
                    state = "<MISSING>"

                zipp = address_list['postalCode']
                if len(zipp) == 5:
                    country_code = "US"
                else:
                    country_code = "CA"
                
                if "openings" in address_list:

                    hours_of_operation = str(address_list['openings']).replace('{', "").replace('}', "").replace("'","").replace(',','')
                else:
                    hours_of_operation = "<MISSING>"
            
                store = []
                result_coords.append((latitude, longitude))
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append("<MISSING>") 
                store.append(phone)
                store.append("<MISSING>")
                store.append(latitude)
                store.append(longitude)
                store.append(hours_of_operation)
                store.append("<MISSING>")

                if store[2] in addresses:                   
                    continue
                addresses.append(store[2])

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield  store

            else:

                pass

               
            
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
