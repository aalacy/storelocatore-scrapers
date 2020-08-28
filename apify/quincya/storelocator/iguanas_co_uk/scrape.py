from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import json
import time
from random import randint
import re
from sgselenium import SgSelenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    driver = SgSelenium().chrome()
    time.sleep(2)

    base_link = "https://api.casualdininggroup.uk/pagedata?brandKey=lasiguanas&path=/spaces/6qprbsfbbvrl/entries?access_token=30ad3e38f991a61b137301a74d5a4346f29fa442979b226cbca1a85acc37fc1c%26select=fields.title,fields.slug,fields.addressLocation,fields.storeId,fields.storeCodeFishBowl,fields.eeRestaurantId,fields.hours,fields.alternativeHours,fields.services,fields.amenities,fields.addressLine1,fields.addressLine2,fields.addressCity,fields.county,fields.postCode,fields.takeawayDeliveryServices,fields.takeawayCollectionService,fields.collectionMessage%26content_type=location%26include=10%26limit=1000"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    data = []

    locator_domain = "iguanas.co.uk"

    stores = json.loads(base.text)["items"]

    for store in stores:
        slug = store["fields"]["slug"]
        link = "https://www.iguanas.co.uk/restaurants/" + slug
        print(link)

        api_link = "https://api.casualdininggroup.uk/pagedata?brandKey=lasiguanas&path=/spaces/6qprbsfbbvrl/entries?access_token=30ad3e38f991a61b137301a74d5a4346f29fa442979b226cbca1a85acc37fc1c%26select=fields%26content_type=location%26fields.slug=" + slug + "%26include=10"
        
        req = session.get(api_link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        store = json.loads(base.text)["items"][0]['fields']

        location_name = "Las Iguanas " + store['title']
        if "coming soon" in location_name.lower():
        	continue
        try:
            street_address = (store['addressLine1'] + " " + store['addressLine2']).strip()
        except:
            street_address = store['addressLine1'].strip()
        city = store['addressCity']
        state = store['county']
        zip_code = store['postCode']
        country_code = "GB"
        store_number = store['storeId']
        location_type = "<MISSING>"
        phone = store['phoneNumber']
        latitude = store['addressLocation']['lat']
        longitude = store['addressLocation']['lon']

        try:
            hours_of_operation = store['openingHours'].replace("\n", " ")
            hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
        except:
            driver.get(link)
            time.sleep(randint(2,3))
            element = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
              (By.CLASS_NAME, "location-tabbed__description")))
            time.sleep(randint(2,4))

            base = BeautifulSoup(driver.page_source,"lxml")
            
            script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
            store = json.loads(script)

            try:
              hours_of_operation = ""
              raw_hours = store['openingHoursSpecification']
              for hours in raw_hours:
                day = hours['dayOfWeek']
                if len(day[0]) != 1:
                  day = ' '.join(hours['dayOfWeek'])
                opens = hours['opens']
                closes = hours['closes']
                if opens != "" and closes != "":
                  clean_hours = day + " " + opens + "-" + closes
                  hours_of_operation = (hours_of_operation + " " + clean_hours).strip()
            except:
              hours_of_operation = "<MISSING>"
        if "Our" in hours_of_operation:
        	hours_of_operation = hours_of_operation[:hours_of_operation.find("Our")].strip()
        	
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    try:
    	driver.close()
    except:
    	pass
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
