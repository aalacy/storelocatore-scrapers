import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sys
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ezmart_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url= "https://gpminvestments.com/store-locator/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    # logger.info(soup)
    # exit()
    k= soup.find_all("script",{"type":"text/javascript"})
    
   

    for i in k:
        if "var wpgmaps_localize_marker_data" in i.text:
            response_json = json.loads(i.text.split("var wpgmaps_localize_marker_data =")[1].strip().split("}}};")[0]+"}}}")
            
            for i in (response_json['7'].keys()):
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), " ".join(str(response_json['7'][i]['address']).split(" ")[1:]))
                tem_var = []
                state_list = re.findall(r'([A-Z]{2})', str(response_json['7'][i]['address'].replace("US","")))
                raw_address  = response_json['7'][i]['address']
                # logger.info( response_json['7'][i]['address'])
                lat = st = response_json['7'][i]['lat']
                lng = st = response_json['7'][i]['lng']
             

                if us_zip_list:
                    zip1 = us_zip_list[-1]
                else:
                    zip1 = "<MISSING>"

                if state_list:
                    state = state_list[-1]
                else:
                    state = "<MISSING>"
                tem_var.append("https://ezmart.com")
                tem_var.append(response_json['7'][i]['title'])
                tem_var.append("<INACCESSIBLE>")
                tem_var.append("<INACCESSIBLE>")
                tem_var.append(state)
                tem_var.append(zip1)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append("<MISSING>")
                tem_var.append(raw_address)
                tem_var.append("https://gpminvestments.com/store-locator/")
                # logger.info(tem_var)
                return_main_object.append(tem_var)
            

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


