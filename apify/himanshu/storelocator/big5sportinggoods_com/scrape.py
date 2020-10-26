import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('big5sportinggoods_com')




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
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 1000
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # logger.info(search.current_zip)

        # logger.info("zip_code === ",lat)
        base_url= "http://big5sportinggoods.com/store/integration/find_a_store.jsp?storeLocatorAddressField="+str(search.current_zip)+"&miles=100&lat="+str(lat)+"&lng="+str(lng)+"&showmap=yes"
        try:
            r = session.get(base_url)
        except:
            pass
        soup= BeautifulSoup(r.text,"lxml")
        a = (soup.find_all("div",{"class":"store-address"}))
        # logger.info(a)
        current_results_len = len(a)
        c = (soup.find_all("input",{"name":"lngHidden"}))
        b = (soup.find_all("input",{"name":"latHidden"}))
        for index,i in enumerate(a):
            location_name = (list(i.stripped_strings)[0])
            street_address = (list(i.stripped_strings)[1].encode('ascii', 'ignore').decode('ascii').strip())
            city = list(i.stripped_strings)[2].split(",")[0].encode('ascii', 'ignore').decode('ascii').strip()
            state = (list(i.stripped_strings)[2].split(",")[1].split( )[0].encode('ascii', 'ignore').decode('ascii').strip())
            zip1 = (list(i.stripped_strings)[2].split(",")[1].split( )[1].encode('ascii', 'ignore').decode('ascii').strip())
            phone = (list(i.stripped_strings)[4].encode('ascii', 'ignore').decode('ascii').strip())
            hours = (list(i.stripped_strings)[6:13])
            hours_of_operation = (''.join(hours))
            latitude = b[index]['value']
            longitude = c[index]['value']
            result_coords.append((latitude, longitude))
            store = []
            store.append("https://big5sportinggoods.com/")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zip1)   
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(base_url)
            
            if store[2] in addresses :
                continue
            addresses.append(store[2])
            yield store  
            # logger.info("--------------------",store) 
       
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
