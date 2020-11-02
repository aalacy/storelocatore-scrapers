from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('solidcore_co')



def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0].strip()
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():

    driver = get_driver()
    time.sleep(2)

    base_link = "https://www.solidcore.co/studios/"

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

    hrefs = base.find(class_='list-locations').find_all("ul")

    link_list = []
    for href in hrefs:
        lis = href.find_all("li")
        for li in lis:
            link = "https://www.solidcore.co" + li.a['href']
            if "/virtual" not in link:
                if "maple grove" in li.a.text and "cohttp" in link:
                    link = "https://solidcoremsp.co/locations/maple-grove/"
                if "st. louis park" in li.a.text and "cohttp" in link:
                    link = "https://solidcoremsp.co/locations/st-louis-park/"
                link_list.append(link)

    all_store_data = []
    locator_domain = 'solidcore.co'

    total_links = len(link_list)
    for i, link in enumerate(link_list):
        logger.info("Link %s of %s" %(i+1,total_links))
        logger.info(link)
        req = session.get(link, headers = HEADERS)
        time.sleep(randint(2,4))
        try:
            item = BeautifulSoup(req.text,"lxml")
        except (BaseException):
            logger.info('[!] Error Occured. ')
            logger.info('[?] Check whether system is Online.')

        if "/locations/" not in link:

            location_name = item.find('h1').text.replace('  ', ' ').title()

            try:
                addy = item.find(class_='studio-address').text.replace("  ", " ").split('\n')
            except:
                req = session.get(link, headers = HEADERS)
                time.sleep(randint(2,4))
                try:
                    item = BeautifulSoup(req.text,"lxml")
                except (BaseException):
                    logger.info('[!] Error Occured. ')
                    logger.info('[?] Check whether system is Online.')
                addy = item.find(class_='studio-address').text.replace("  ", " ").split('\n')

            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1])

            phone_number = item.find(class_='studio-contact').text.split('\n')[0]

            try:
                gmaps_link = item.find(class_='studio-address').a['href']
                driver.get(gmaps_link)
                time.sleep(randint(8,10))

                map_link = driver.current_url
                at_pos = map_link.rfind("@")
                latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
                longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
            except:
                latitude = '<MISSING>'
                longitude = '<MISSING>'
        else:

            location_name = item.find('h1').text.replace('[solidcore]', '').strip().title()

            street_address = item.find(class_="street-address").text
            city = item.find(class_="locality").text
            if "maple grove" in location_name.lower() or "louis park" in location_name.lower():
                state = "MN"
            zip_code = item.find(class_="postal-code").text

            phone_number = item.find(class_='wpseo-phone').text.replace("Phone:","").strip()

            script_str = str(item.find('script', attrs={'type': 'application/ld+json'}))
            script = script_str[script_str.find("{"):script_str.rfind("]}")+2]
            js = json.loads(script)

            latitude = js['@graph'][-2]['geo']['latitude']
            longitude = js['@graph'][-2]['geo']['longitude']

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, latitude, longitude, hours]
        all_store_data.append(store_data)

    try:
        driver.close()
    except:
        pass

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
