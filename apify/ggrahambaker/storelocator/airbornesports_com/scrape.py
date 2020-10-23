import csv
import os
from sgrequests import SgRequests
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import usaddress
import re
import time
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('airbornesports_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    locator_domain = 'https://airbornesports.com/'
    ext = 'hours-and-pricing/'

    session = SgRequests()
    driver = SgSelenium().chrome()

    req = session.get(locator_domain+ext, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")
    buttons = base.find_all(class_="fusion-button")[1:]
    link_list = []
    for button in buttons:
        href = button['href']
        if "airbornesports.com" in href and "hours" not in href:
            href = href + "hours-and-pricing/"
        if href not in link_list:
            link_list.append(href)

    all_store_data = []
    found_poi = []
    for link in link_list:
        if "hours" not in link:
            continue
        # logger.info(link) 
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        hours = base.find(class_="reading-box-additional").text.replace('\r\n',"").replace('\n', ' ').replace('PM','PM ').replace('DAY','DAY ').replace('DAY S','DAYS')\
        .replace('\xa0','').replace('Night',' ').replace("Open Jump(all ages)","").replace("Open Jump(all ages)9 PM - 11 PM Teen Flight","").replace("Open Jump (all ages)","")\
        .replace("Special HoursNo special hours","").replace("9 PM  - 11 PM  Teen Flight","").replace("College   Coming Soon","")

        hours = (re.sub(' +', ' ', hours)).strip()

        icons = base.find_all(class_="fusion-social-network-icon")
        for i in icons:
            if "tel" in i["href"]:
                phone_number = i["href"].replace('tel:', '')
                break

        href = ""
        for i in icons:
            if "google" in i["href"] or "yelp" in i["href"]:
                href = i["href"]
                break

        if "google" in href:
            start_idx = href.find('/@')
            end_idx = href.find('z/data')

            coords = href[start_idx + 2: end_idx].split(',')

            lat = coords[0]
            longit = coords[1]

            # Get address from gmaps
            driver.get(href)
            time.sleep(10)
            raw_address = driver.find_element_by_xpath("//button[(@data-item-id='address')]").text.split(",")
            street_address = raw_address[0]
            city = raw_address[1].strip()
            state = raw_address[2].split()[0]
            zip_code = raw_address[2].split()[1]
        elif "yelp" in href:
            req = session.get(href, headers = HEADERS)
            base = BeautifulSoup(req.text,"lxml")
            raw_address = list(base.find(class_="lemon--address__373c0__2sPac").stripped_strings)
            street_address = " ".join(raw_address[:-2])
            city = raw_address[-1].split(",")[0].strip()
            state = raw_address[-1].split(",")[1].split()[0]
            zip_code = raw_address[-1].split(",")[1].split()[1]
            if "8800 N Tarrant" in street_address:
                lat = '32.902634'
                longit = '-97.197044'
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'

        location_name = driver.title.replace("- Google Maps","").strip() + " " + city
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'US'

        if street_address not in found_poi:            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours, link]

            all_store_data.append(store_data)
            found_poi.append(street_address)

    for link in link_list:
        if "hours" in link:
            continue
        # logger.info(link)
        if "southjordan" in link:
            ad_link = link + "/contact-us"
            hrs_link = link + "/hourspricing"
            location_name = "Airborne South Jordan"
        elif "lewisville" in link:
            ad_link = link + "contact"
            hrs_link = link + "pricing"
            location_name = "Airborne Lewisville"
        else:
            raise

        req = session.get(ad_link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        raw_address = list(base.find(class_="sqs-block-content").stripped_strings)[1:]
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0].strip()
        state = raw_address[1].split(",")[1].strip()
        zip_code = raw_address[1].split(",")[2].strip()
        country_code = 'US'

        try:
            phone = re.findall("[[(\d)]{3}-[\d]{3}-[\d]{4}", str(base.find(class_="sqs-block-content")))[0]
        except:
            phone = "<MISSING>"

        store_number = '<MISSING>'
        location_type = '<MISSING>'

        js = base.find(class_="sqs-block map-block sqs-block-map sized vsize-12")['data-block-json']
        store = json.loads(js)

        lat = store['location']['mapLat']
        longit = store['location']['mapLng']

        req = session.get(hrs_link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        raw_hours = base.find(class_="sqs-layout sqs-grid-12 columns-12").find_all(class_="row sqs-row")[1]
        if "day" not in str(raw_hours).lower():
            raw_hours = base.find(class_="sqs-layout sqs-grid-12 columns-12").find(class_="row sqs-row")

        hours = raw_hours.text.replace('PM','PM ').replace('day','day ').replace('DAY','DAY ').replace('Hours','').strip()
        hours = (re.sub(' +', ' ', hours)).strip()

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, link]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
