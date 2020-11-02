import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('rosesdiscountstores_com__bill')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object = []
    r = session.get("https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=53.1234%2C-46.45623&southwest=-4.1234%2C-149.486512")
    data = r.json()["locations"]
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.rosesdiscountstores.com/")
        store.append(store_data["name"])
        try:
            st = (" ".join(store_data["visibleAddress"].split(",")[:-3]))
        except:
            st = (" ".join(store_data["address"].split(",")[:-3]))
            # logger.info(st)
        if "38703" in store_data["postcode"]:
            st = "3001 US Highway 82, East St"
        store.append(st)
        if store[-1] == "":
            store[-1] = store_data["address"].split(",")[0]
        store.append(store_data["city"] if store_data["city"] else store_data["address"].split(",")[1])
        store.append(store_data["region"])
        store.append(store_data["postcode"] if store_data["postcode"] != "" else store_data["address"].split(",")[-2].split(" ")[-1])
        if len(store[-1]) <= 3 or len(store[-1]) >=7:
            store[-1] = "<MISSING>"
        store.append("US")
        store.append("<MISSING>")
        try :
            phone = store_data["contacts"]["con_wg5rd22k"]["text"]
        except :
            phone = "<MISSING>"
        store.append(phone)
        store.append(store_data["name"])
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        if type(store_data["hours"]) == dict:
            for key in store_data["hours"]["hoursOfOperation"]:
                hours = hours + key + " " +store_data["hours"]["hoursOfOperation"][key].replace("-"," to ") + " "
        elif store_data["hours"] == "hrs_a4db656x":
            hours = "mon 9 am to 6 pm tue 9 am to 6 pm wed 9 am to 6 pm thurs 9 am to 6 pm fri 9 am sat 6 am to 9pm sun 12 am to 6 pm"
        else:
            hours = store_data["hours"]
        store.append(hours.strip() if hours else "<MISSING>")
        store.append("<MISSING>")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]        
        yield store 
    
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
