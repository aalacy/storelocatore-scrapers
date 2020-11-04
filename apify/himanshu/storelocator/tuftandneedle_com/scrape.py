import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tuftandneedle_com')

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
    return_main_object = []
    addresses = []
    addresses1 =[]
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "accept": "*/*",
        "content-type": "application/json",
        # "Host": "api.tuftandneedle.com",
        # "x-requested-with":"XMLHttpRequest",
        # "Origin": "https://www.tuftandneedle.com",
        "Referer": "https://www.tuftandneedle.com/stores/",
        # "X-API-Key": "cd39a8f842ccdf6e753f4129381a18b9",
    }

    # base_url = "https://www.seattlesbest.com"

    while zip_code:
        result_coords = []

        #logger.info("zip_code === "+zip_code)
        data = '{"operationName":"GetStores","variables":{"geoSearchParams":{"zipcode":"'+str(zip_code)+'","radius":"500"}},"query":"query GetStores($geoSearchParams: GeoSearchParams!) { getStores(geoSearchParams: $geoSearchParams) {   results {     retailStores {       name       uuid       hours       lat       lng       serviceArea       prettyName       comingSoon       address {         line1         line2         city         state         zip         __typename       }       storeType       ... on StoreWithSearchLocation {         distance         __typename       }       capabilities {         type         availableInventory         __typename       }       __typename     }     partnershipStores {       name       uuid       hours       lat       lng       prettyName       serviceArea       phoneNumber       address {         line1         line2         city         state         zip         __typename       }       storeType       ... on StoreWithSearchLocation {         distance         __typename       }       capabilities {         type         availableInventory         __typename       }       __typename     }     searchLocation {       lat       lng       __typename     }     __typename   }   __typename } } " }'
        location_url = "https://api.tuftandneedle.com/api/graphql"
        try:
            json_data = session.post(location_url,headers=headers,data=data).json()
        except:
            continue
        # soup = BeautifulSoup(r.text, "lxml")
           

        # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")

        # current_results_len = int(soup.find("stores",{"count":re.compile("")})["count"])        # it always need to set total len of record.

        locator_domain = "https://www.tuftandneedle.com/"
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = "<MISSING>"
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = "<MISSING>"
        # if json_data['data']['getStores']["results"]['retailStores']
        
        # logger.info("===============================",current_results_len)
        # logger.info(json_data['data'])
        if json_data['data'] != None:
            current_results_len = len(json_data['data']['getStores']["results"]['retailStores']+json_data['data']['getStores']["results"]['partnershipStores'])
            
            for loc in json_data['data']['getStores']["results"]['partnershipStores']:
                location_name = loc['name']
                hours = " ".join(loc['hours']).replace("Call store for hours*","")
                if hours:
                    hours_of_operation = hours
                else:
                    hours_of_operation ="<MISSING>"


                latitude = str(loc['lat'])
                longitude = str(loc['lng'])
                state = loc['address']['state']
                zipp = loc['address']['zip']
                city =  loc['address']['city']
                line2=''
                if "phoneNumber" in loc:
                    phone =  loc['phoneNumber']
                else:
                    phone = ''
                if loc['address']['line2'] != None:
                    line2 = loc['address']['line2']

                street_address = loc['address']['line1']+ ' ' +line2
                location_type = loc['storeType']
                 
                store1 = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                if store1[2]  in addresses1:
                    continue

                addresses1.append(store1[2])
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store1]

                # logger.info("data = partnershipStores " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                yield store1

            for loc in json_data['data']['getStores']["results"]['retailStores']:
                street_address = loc['address']['line1']+ ' ' + loc['address']['line2']
                location_name = loc['name']
                state = loc['address']['state']
                zipp = loc['address']['zip']
                city =  loc['address']['city']
                latitude = str(loc['lat'])
                longitude = str(loc['lng'])
                if "phoneNumber" in loc:
                    phone =  loc['phoneNumber']
                else:
                    phone = ''
                hours_of_operation = " ".join(loc['hours'])
                location_type= loc['storeType']
                result_coords.append((latitude, longitude))
                
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                if store[2]  in addresses:
                    continue

                addresses.append(store[2])
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # logger.info("data = retailStores" + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                yield store

        if current_results_len < MAX_RESULTS:
            #logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
