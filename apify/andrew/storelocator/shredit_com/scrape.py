import csv
import json
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver', options=options)

BASE_URL = 'https://www.shredit.com'
MISSING = '<MISSING>'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def clean(string, value):
    return MISSING if string == value else string

def fetch_data():
    data = []
    driver.get('https://www.shredit.com/en-us/service-locations')
    driver.refresh()
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.location-select ul > li > a"))
    )
    store_data = [
        (
            a_tag.get_attribute('innerText'),
            a_tag.get_attribute('data-node-id'),
            a_tag.get_attribute('href')
        )
        for a_tag in driver.find_elements_by_css_selector("ul.location-select ul > li > a")
    ]
    for location_name, store_number, store_url in store_data:
        driver.get(store_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        script = json.loads(
            soup.select_one('script[type="application/ld+json"]').text
        )
        street_address = clean(script.get('address').get('streetAddress'), None)
        city = clean(script.get('address').get('addressLocality'), None)
        state = clean(script.get('address').get('addressRegion'), None)
        zipcode = clean(script.get('address').get('postalCode'), None)
        country_code = script.get('address').get('addressCountry')
        phone = script.get('telephone')
        latitude = clean(script.get('geo').get('latitude'), '0')
        longitude = clean(script.get('geo').get('longitude'), '0')
        hours_of_operation = clean(driver.find_elements_by_css_selector('p.service-hours')[-1].text.strip(), '')
        data.append([
            BASE_URL,
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
