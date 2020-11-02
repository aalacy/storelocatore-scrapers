import csv
from sgrequests import SgRequests
import json
# from datetime import datetime
# import phonenumbers
from bs4 import BeautifulSoup
import re
# import unicodedata
# import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fivestarseniorliving_com')




session = SgRequests()

def write_output(data):
    with open('data.csv',newline="", mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = "https://www.fivestarseniorliving.com/"
    addresses = []
    country_code = "US"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    store_number = "<MISSING>"
    location_type = "<MISSING>"
    r = session.get("https://www.googletagmanager.com/gtm.js?id=GTM-MFVKXDD",headers=headers)
    map_list = "".join(r.text.split('"vtp_map":')[1].split("},")[0].split('["list",')[1].split("]]")[0]+"]").split("],")
    for i in map_list:
        loc = str(i).split(",")
        phone = loc[-1].replace('"',"").replace("]","").strip()
        if "http" not in loc[2]:
            page_url = "https://www.fivestarseniorliving.com"+loc[2].replace('"',"").replace('\\',"").strip()
        else:
            page_url = loc[2].replace('"',"").replace('\\',"").strip()
        # logger.info(page_url)
        r1 = session.get(page_url,headers=headers)
        soup = BeautifulSoup(r1.text,"lxml") 
        try:
            script = json.loads(soup.find("script",{"type":"application/ld+json"}).text ) 
        except:
            continue
        if "address" in script["@graph"][0]:
            location_name = script["@graph"][0]["name"]
            phone = script["@graph"][0]["telephone"]
            street_address = script["@graph"][0]["address"]["streetAddress"].replace("Naples, FL 34113","").strip()
            city = script["@graph"][0]["address"]["addressLocality"]
            state = script["@graph"][0]["address"]["addressRegion"]
            zipp = script["@graph"][0]["address"]["postalCode"]
            country_code = script["@graph"][0]["address"]["addressCountry"]
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses:
                addresses.append(str(store[1]) + str(store[2]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

        # except:
        #     pass
        
        
            #


       


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
