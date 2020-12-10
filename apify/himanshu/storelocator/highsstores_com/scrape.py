# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import http.client
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('highsstores_com')



session = SgRequests()

http.client._MAXHEADERS = 1000


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        
    }

    base_url = "https://www.highs.com/"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        try:
            location_url = "https://www.highs.com/wp-admin/admin-ajax.php?action=store_search&lat="+str(lat)+"&lng="+str(lng)+"&max_results=25&search_radius=50&autoload=1"
        except:
            continue
        r = session.get(location_url, headers=headers)
        json_data = r.json()
       
        current_results_len = len(json_data)
        for i in json_data:
            location_name = i['store'].replace("&#8217;","’").replace("&#8211;","-")
            street_address = i['address']
            city = i['city']
            state = i['state']
            zipp = i['zip']
            store_number = i['id']
            phone = i['phone']
            latitude = i['lat']
            longitude = i['lng']
            table_data = [[cell.text for cell in row("td")]
                         for row in BeautifulSoup(i['hours'], features = "lxml")("tr")]
            hours_of_operation =  json.dumps(dict(table_data)).replace("{","").replace("}","").replace('"','').replace(',','')
            store = []
            result_coords.append((latitude, longitude))
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude )
            store.append(longitude )
            store.append(hours_of_operation)
            store.append("https://www.highs.com/locations/")
            if store[2] in addresses:
                continue     
            addresses.append(store[2])
            yield store
        

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
