import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('extendicare_com')


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # addresses = []
    country_code = "CA"
    headers = {
            'accept':'*/*',
            'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
    locator_domain = "https://www.extendicare.com/"
    r= session.get("https://www.extendicare.com/contact/find/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    table = soup.find("table",{"id":"locationTable"})
    for loc in table.find("tbody").find_all("tr"):
        store_number = loc["data-id"]
        location_name = loc["data-name"]
        street_address= loc["data-address"]
        city = loc["data-city"]
        state = loc["data-province"]
        zipp=loc["data-postal"]
        phone= loc["data-phone"]
        try:
            location_type = loc["data-type"]
        except:
            location_type = "<MISSING>"
        if "http://" == loc["data-url"].strip():
            page_url = "<MISSING>"
        else:
            page_url = loc["data-url"]
        latitude = loc["data-latitude"]
        longitude =loc["data-longitude"]
        hours_of_operation = "<MISSING>"
    
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        # if str(str(store[1])+str(store[2])) not in addresses :
        #     addresses.append(str(store[1])+str(store[2]))

        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store

    

   
   


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
