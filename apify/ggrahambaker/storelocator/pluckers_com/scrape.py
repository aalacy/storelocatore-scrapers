import csv
import os
from sgselenium import SgSelenium
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import time
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

#helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    return city, state, zip_code

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    data = []
    driver = SgSelenium().chrome()
    driver1 = SgSelenium().chrome()

    locator_domain = 'https://www.pluckers.com/'
    ext = 'locations'
    driver.get(locator_domain + ext)
    time.sleep(6)

    store_name = driver.find_elements_by_css_selector('div.storepoint-location')

    all_store_data = []
    for store in store_name:
        location_name = store.find_element_by_css_selector('div.storepoint-name').text

        phone_number = store.find_elements_by_css_selector('a')[1].text
        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        link = store.find_elements_by_tag_name('a')[-2].get_attribute("href")
        if "tel" in link:
            link = store.find_elements_by_tag_name('a')[-1].get_attribute("href")
        print(link)
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        hours = '<MISSING>'
        raw_hours = base.find_all(class_="address-phone w-richtext")[-1].text.strip()
        if "pm" in raw_hours or "am" in raw_hours:
            hours = raw_hours[:raw_hours.rfind("m")+1].replace("pm","pm ").replace("Hours","Hours ").strip()
        if "coming" in raw_hours.lower():
            continue

        # address
        street_address = base.find(class_='address-phone w-richtext').p.text.replace("Â","").replace("Rd,","Rd").strip()
        city_line = base.find(class_='address-phone w-richtext').find_all("p")[1].text.replace("\xa0"," ").replace("TX,","TX").replace("Austin TX","Austin, TX").strip()
        if ") " in street_address:
            street_address = base.find(class_='address-phone w-richtext').find_all("p")[2].text.replace("Â","").replace("Rd,","Rd").strip()
            city_line = base.find(class_='address-phone w-richtext').find_all("p")[3].text.replace("\xa0"," ").replace("TX,","TX").replace("Austin TX","Austin, TX").strip()
        city, state, zip_code = addy_extractor(city_line)

        driver1.get(link)
        time.sleep(2)

        try:
            geo = re.findall(r'{lat.+lng:.+}', driver1.page_source)[0]
            lat = geo.split(":")[1].split(",")[0].strip()
            longit = geo.split(":")[-1].split("}")[0].strip()
            if not lat:
                lat = '<MISSING>'
                longit = '<MISSING>'
        except:
            lat = '<MISSING>'
            longit = '<MISSING>'
            
        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
        
    # End scraper

    driver.quit()
    driver1.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
