import csv
import re
import time
from sgselenium import SgSelenium

driver = SgSelenium().chrome()
time.sleep(2)

BASE_URL = 'https://cava.com/locations'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    driver.get(BASE_URL)
    time.sleep(8)
    stores = driver.find_elements_by_css_selector('div.vcard')
    for store in stores:
        location_name = store.find_element_by_css_selector('h3').text
        street_address = store.find_element_by_css_selector('div.street-address').text
        city = store.find_element_by_css_selector('span.locality').text.replace(',', '')
        state = store.find_element_by_css_selector('span.region').text
        zipcode = store.find_element_by_css_selector('span.postal-code').text
        try:
            hours_of_operation = store.find_element_by_css_selector('p.copy').text.replace("Hours:","").strip()
        except:
            note = store.find_element_by_css_selector('.location-note').text
            if "coming" in note.lower():
                continue
            if "close" in note.lower():
                hours_of_operation = note
        try:
            phone = store.find_element_by_css_selector('div.vcard > div.adr > div > a').text
        except:
            phone = '<MISSING>'
        try:
            store_number = store.find_element_by_css_selector("div.adr ~ p > a[href*='order.cava.com']").get_attribute('href')
            store_number = re.findall(r'stores\/{1}(\d*)', store_number)[0]
        except:
            store_number = '<MISSING>'
        data.append([
            'cava.com',
            BASE_URL,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            store_number,
            phone,
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            hours_of_operation
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
