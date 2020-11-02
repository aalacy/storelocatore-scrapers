from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
import json
import re
from random import randint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('alexisbittar_com')




def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    base_link = "https://www.alexisbittar.com/pages/store-location"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(2,3))
    try:
        base = BeautifulSoup(req.text,"lxml")
        logger.info("Got today page")
    except (BaseException):
        logger.info('[!] Error Occured. ')
        logger.info('[?] Check whether system is Online.')

    items = str(base.find(class_="rte")).split("<strong>")[1:]

    data = []
    for item in items:
        raw_data = item.split("<br/>")
        location_name = raw_data[0][:raw_data[0].find("<")].strip()
        for i in range(len(raw_data)):
            str_row = raw_data[i]
            clean_row = BeautifulSoup(str_row,"lxml")
            prev_clean_row = BeautifulSoup(raw_data[i-1],"lxml")

            if "," in str_row:
                street_address = prev_clean_row.text.strip()
                if "\n" in street_address:
                    street_address = street_address[street_address.find("\n")+2:].strip()
                city_line = str_row.replace("\xa0","").strip()
                city = city_line[:city_line.find(",")].strip()
                state = city_line[city_line.find(",")+1:city_line.find(",")+4].strip()
                zip_code = city_line[-6:].strip()
            elif "Hours" in str_row or "day " in str_row:
                hours = clean_row.text.replace("Store Hours:","").replace("\n","").replace("Appointment","Appointment ").replace("pm","pm ").replace("\xa0","").strip()
                if "(" in hours:
                    phone = hours[hours.find("("):].strip()
                    hours = hours[:hours.find("(")].strip()
                    
            elif "(" in str_row:
                phone = clean_row.text.strip()

        locator_domain = "alexisbittar.com"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = hours

        data.append([locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

