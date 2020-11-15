import csv
import json
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests

from sgselenium import SgChrome

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = 'https://www.shredit.com'
MISSING = '<MISSING>'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def clean(string, value):
    return MISSING if string == value else string

def fetch_data():
    data = []
    driver = SgChrome().chrome()

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    driver.get('https://www.shredit.com/en-us/service-locations')
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".branchList"))
    )

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    store_data = [
        (
            a_tag.find(class_='address').text.strip(),
            a_tag.find(class_='cardNumber').text.strip(),
            a_tag.find('a')['href']
        )
        for a_tag in soup.find(id="branchList").find_all("li")
    ]
    for location_name, store_number, store_url in store_data:
        req = session.get(store_url, headers = HEADERS)
        soup = BeautifulSoup(req.text,"lxml")
        script = json.loads(
            soup.find_all('script', attrs={'type': "application/ld+json"})[-1].text
        )
        street_address = clean(script.get('address').get('streetAddress'), None).replace("Suite"," Suite").replace("STE","Ste").replace("Ste"," Ste").replace("Unit"," Unit")

        if not street_address:
            script = json.loads(
                soup.find_all('script', attrs={'type': "application/ld+json"})[0].text
            )
        street_address = clean(script.get('address').get('streetAddress'), None).replace("Suite"," Suite").replace("STE","Ste").replace("Ste"," Ste").replace("Unit"," Unit")
        street_address = (re.sub(' +', ' ', street_address)).strip()
        city = clean(script.get('address').get('addressLocality'), None)
        state = clean(script.get('address').get('addressRegion'), None)
        zipcode = clean(script.get('address').get('postalCode'), None)
        if not zipcode:
            zipcode = MISSING
        country_code = "US"
        phone = script.get('telephone')
        if not phone:
            script = json.loads(
                soup.find_all('script', attrs={'type': "application/ld+json"})[0].text
            )
        phone = script.get('telephone')
        if "844-945-1370" in phone:
            phone = "800-697-4733"
        latitude = clean(script.get('geo').get('latitude'), '0')
        longitude = clean(script.get('geo').get('longitude'), '0')
        try:
            latitude = format(float(latitude), '.5f')
            longitude = format(float(longitude), '.5f')
        except:
            pass
        hours_of_operation = clean(soup.find_all(class_='service-hours')[-1].text.replace("\r\n"," ").strip(), '')
        hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
        data.append([
            BASE_URL,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            country_code,
            store_number,
            phone,
            MISSING,
            latitude,
            longitude,
            hours_of_operation
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
