import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('holidaytouch_com')


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
    country_code = "US"
    headers = {
            'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            # 'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
        }
    locator_domain = "https://www.holidaytouch.com/"
    r= session.get("https://www.holidaytouch.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    footer = soup.find("footer",class_="footer")
    for ul in footer.find_all("ul",class_="footer-top__list"):
        for state_link in ul.find_all("a",class_="footer-top__link"):
            state_link_url = state_link["href"]
            # logger.info(state_link.text)
            r1 = session.get("https://www.holidaytouch.com"+state_link_url,headers=headers)
            soup1 = BeautifulSoup(r1.text,"lxml")
            script = json.loads(soup1.find("script",text=re.compile("var communities = ")).text.split("var communities = ")[1].split("];")[0]+"]")
            for x in script:
                longitude = x["Longitude"]
                latitude = x["Latitude"]
                location_name = x["Name"].strip()
                street_address = x["Address"]
                city = x["City"]
                state = x["State"]
                zipp = x["ZipCode"]
                phone = x["PhoneNumber"]
                page_url = "https://www.holidaytouch.com/our-communities/"+location_name.replace(" ","-").lower().strip()
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                hours_of_operation = "Monday-Sunday 7:30 am - 7:30 pm"
                
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                # if str(str(store[1])+str(store[2])) not in addresses :
                #     addresses.append(str(store[1])+str(store[2]))

                store = [str(x).strip() if x else "<MISSING>" for x in store]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

    
    
   
   


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
