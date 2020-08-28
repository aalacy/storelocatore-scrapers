from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sgselenium import SgSelenium


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    base_link = "https://fitnessconnection.com/locations/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    main_links = []
    main_items = base.find_all(class_="club column small-12 medium-4")
    for main_item in main_items:
        main_link = main_item.a['href']
        raw_address = str(main_item.find(class_="address-wrapper").a)
        raw_address = raw_address[raw_address.find('blank">')+7:raw_address.rfind('<')]
        main_links.append([main_link,raw_address])

    data = []

    driver = SgSelenium().chrome()
    time.sleep(2)

    total_links = len(main_links)
    for i, raw_link in enumerate(main_links):
        print("Link %s of %s" %(i+1,total_links))

        link = raw_link[0]
        raw_address = raw_link[1]

        req = session.get(link, headers = HEADERS)
        item = BeautifulSoup(req.text,"lxml")
        print(link)

        locator_domain = "fitnessconnection.com"

        location_name = item.find("h3").text.replace("-","- ").replace("– NOW OPEN","").replace("– Now Open!","").strip()
        if "coming soon" in location_name.lower():
            continue
        # print(location_name)

        street_address = raw_address[:raw_address.find("<")].strip()
        if ", Austin" in street_address:
            street_address = street_address[:street_address.find(", Austin")].strip()
        city = raw_address[raw_address.find(">")+1:raw_address.rfind(",")].strip()
        state = raw_address[raw_address.rfind(",")+1:raw_address.rfind(" ")].strip()
        zip_code = raw_address[raw_address.rfind(" ")+1:].strip()
        if not zip_code:
            zip_code = state.split()[1].strip()
            state = state.split()[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        
        location_type = "<MISSING>"

        try:
            phone = item.find(class_="phone").text.strip()
        except:
            phone = "<MISSING>"

        try:
            raw_hours = item.find(class_="primary-hours").text
            hours_of_operation = raw_hours.replace("\n", " ").replace("\r", "").strip()
        except:
            continue
        
        raw_gps = item.find(class_="address-wrapper").a['href']
        try:
            # print("Opening gmaps..")
            driver.get(raw_gps)
            time.sleep(randint(6,8))

            map_link = driver.current_url
            at_pos = map_link.rfind("@")
            latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
            longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
        except:
            print('Map not found..skipping')
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
