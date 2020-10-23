from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('backwoods_com')



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    base_link = "https://backwoods.com/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
        logger.info("Got today page")
    except (BaseException):
        logger.info('[!] Error Occured. ')
        logger.info('[?] Check whether system is Online.')

    locs = base.find(class_="footer-block-content").find_all(class_="col-6 col-md-4 col-lg-2")[-2].find_all("li")

    data = []
    all_links = []
    for loc in locs:
        link = "https://backwoods.com" + loc.a['href']
        all_links.append(link)

    for link in all_links:
        req = session.get(link, headers = HEADERS)
        time.sleep(randint(1,2))
        try:
            item = BeautifulSoup(req.text,"lxml")
        except (BaseException):
            logger.info('[!] Error Occured. ')
            logger.info('[?] Check whether system is Online.')

        location_name = item.find("h1").text.strip()
        logger.info(location_name)

        locator_domain = "backwoods.com"
        
        raw_address = item.find(class_="col-sm-6").text.strip().replace("\t","").replace("\r\n",",").replace("Ave.,","Ave.").split(",")

        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[2][:-6].strip()
        zip_code = raw_address[2][-6:].strip()

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        try:
            phone =  item.find(class_="button big").text
        except:
            phone = "<MISSING>"

        hours_of_operation = item.find_all(class_="clean-list")[-1].text.replace("\n"," ").replace("day","day ").strip()

        try:
            map_link =item.find_all("iframe")[1]['src']
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


