from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('finks_com')




def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    base_link = "https://www.finks.com/pages/store-directory"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
    except (BaseException):
        logger.info('[!] Error Occured. ')
        logger.info('[?] Check whether system is Online.')

    main_links = []
    main_items = base.find_all(class_="go-link")
    for main_item in main_items:
        main_link = "https://www.finks.com" + main_item['href']
        main_links.append(main_link)

    data = []

    driver = get_driver()
    time.sleep(2)

    for link in main_links:

        req = session.get(link, headers = HEADERS)
        time.sleep(randint(1,2))
        try:
            item = BeautifulSoup(req.text,"lxml")
            logger.info(link)
        except (BaseException):
            logger.info('[!] Error Occured. ')
            logger.info('[?] Check whether system is Online.')
        time.sleep(randint(1,2))

        locator_domain = "finks.com"

        location_name = item.find("h1").text.strip()
        logger.info(location_name)

        try:
            raw_address = item.find("address").text.strip().split("\n")
        except:
            continue
        if len(raw_address) == 3:
            street_address = (raw_address[0].strip() + " " + raw_address[1].strip()).strip()
        else:
            street_address = raw_address[0].strip()        

        city_line = raw_address[-1]
        if street_address == location_name:
           street_address = raw_address[1]
        city = city_line[:city_line.find(",")].strip()
        state = city_line[city_line.find(",")+1:city_line.rfind(" ")].strip()
        zip_code = city_line[city_line.rfind(" ")+1:].strip()
        country_code = "US"
        store_number = "<MISSING>"
        
        location_type = "<MISSING>"

        try:
            phone = item.find(class_="location-contact__method location-contact__method--phone").text.strip()
        except:
            phone = "<MISSING>"

        raw_hours = item.find(class_="location-contact__text").text
        raw_hours = raw_hours[raw_hours.find(" Hours"):raw_hours.find("\nContact")].strip()
        hours_of_operation = raw_hours[:raw_hours.rfind("\n")].replace("\n", " ").replace("Hours","").strip()

        try:
            raw_gps = item.find(class_="go-link")["href"]
            lat_pos = raw_gps.find("@")+1
            latitude = raw_gps[lat_pos:raw_gps.find(",", lat_pos)].strip()
            long_pos = raw_gps.find(",", lat_pos)
            longitude = raw_gps[long_pos+1:raw_gps.find(",",long_pos+3)].strip()

            if not latitude[4:6].isnumeric() or not longitude[4:6].isnumeric():
                raise
        except:
            try:
                logger.info("Opening gmaps..")
                driver.get(raw_gps)
                time.sleep(randint(6,8))

                map_link = driver.current_url
                at_pos = map_link.rfind("@")
                latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
                longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
            except:
                logger.info('Map not found..skipping')
                latitude = "<MISSING>"
                longitude = "<MISSING>"

        location_data = [locator_domain, link, location_name, street_address, city, state, zip_code,
                        country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

        data.append(location_data)
    
    try:
        driver.close()
    except:
        pass

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()