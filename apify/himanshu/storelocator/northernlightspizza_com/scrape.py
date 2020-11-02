import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('northernlightspizza_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        # "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.northernlightspizza.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "https://www.northernlightspizza.com/locations/"


  
    r= session.get('https://www.northernlightspizza.com/locations/',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    json_data = json.loads(soup.find(lambda tag: (tag.name == "script") and "var wpgmaps_localize_marker_data" in tag.text).text.split("var wpgmaps_localize_marker_data =")[1].split(";")[0])
    for key,value in json_data.items():
        for key1,value1 in json_data[key].items():
            data = json_data[key][key1]
            latitude = data['lat']
            longitude = data['lng']


            location_name = data['title']
            street_address = data['address'].split(",")[0]
            city = data['address'].split(",")[1]
            state = data['address'].split(",")[2].split(" ")[1]
            try:
                zipp = data['address'].split(",")[2].split(" ")[2]
            except:
                zipp = "<MISSING>"
            # logger.info(data['desc'].split("\n"))
            if "Hours" in data['desc'].split("\n"):
                try:
                    phone = data['desc'].split("\n")[0]
                except:
                    phone=""
                hours_of_operation = " ".join(data['desc'].split("\n")[2:])
            else:
                try:
                    phone = data['desc'].split("\n")[1].replace("OPENING IN JUNE!!","515-967-4300")
                except:
                    phone=""
                hours_of_operation = "<MISSING>"
            if "1821 1st Ave E" in street_address:
                zipp="50208"
            if "4217 Frederick Avenue" in street_address:
                zipp="64506"
            if "158 Long Road" in street_address:
                zipp="63005"
           
   
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone.replace("Dine-In, Carryout & Delivery!",""), location_type, latitude, longitude, hours_of_operation,page_url]
            store = ["<MISSING>" if x == "" else x for x in store]

            # logger.info("data = " + str(store))
            # logger.info(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            store = [x.replace("–","-") for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
            # logger.info(store)
    
    # return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
