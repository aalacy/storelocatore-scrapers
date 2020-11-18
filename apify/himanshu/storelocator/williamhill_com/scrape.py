import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('williamhill_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess123=[]
    #v
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['uk'])
    MAX_RESULTS = 25
    MAX_DISTANCE = 25
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    locator_domain = base_url = "https://www.williamhill.com/"
    headers= {
            'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
            'content-type': "application/x-www-form-urlencoded",
    }
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        data='lat='+str(lat)+'&lng='+str(lng)
        locator_domain ='https://www.williamhill.com/'
        r = session.post("http://shoplocator.williamhill/results",data=data,headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        json_data = soup.find(lambda tag: (tag.name == "script" ) and "window.lctr.center" in tag.text.strip())
        if json_data != None:
            try:
                json_data1 = json_data.text.split("window.lctr.results.push(")
            except:
                coord = search.next_coord()
                search.max_distance_update(MAX_DISTANCE)
                continue
            for data in json_data1[1:]: 
                j_data = json.loads(data.replace("});",'}'))
                location_name=j_data['name']
                latitude = j_data['latitude']
                longitude =j_data['longitude']
                zipp =j_data['post_code']
                street_address = j_data['street_no']+' '+j_data['street']
                city = '<MISSING>'
                if j_data['city']:
                    city = j_data['city']
                else:
                    city = j_data['county']
                if city:
                    city=city
                else:
                    city ="<MISSING>"

                state='<MISSING>'
                phone =j_data['phone']
                country_code="UK"
                page_url="<MISSING>"
                location_type="<MISSING>"
                store_number = "<MISSING>"
                try:
                    hours_of_operation='Monday '+j_data['mon_open']+' - '+j_data['mon_close']+ ' Tuesday '+j_data['tue_open']+' - '+j_data['tue_close']+ ' Wednesday '+j_data['wed_open']+' - '+j_data['wed_close']+' Thursday '+j_data['thu_open']+' - '+j_data['thu_close']+ ' Friday '+j_data['fri_open']+' - '+j_data['fri_close']+' Saturday '+j_data['sat_open']+' - '+j_data['sat_close']+ ' Sunday '+j_data['sun_open']+' - '+j_data['sun_close']
                except:
                    hours_of_operation="<MISSING>"
                store = [locator_domain, location_name.replace('\n', ' '), street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                if store[2]  in addressess123:
                    continue
                addressess123.append(store[2])
                # logger.info(store)
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
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



