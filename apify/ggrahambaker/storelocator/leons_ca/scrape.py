import csv
import os
from sgselenium import SgSelenium
import json
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://leons.ca'
    ext = '/apps/store-locator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    alert_obj = driver.switch_to.alert
    alert_obj.accept()

    element = driver.find_element_by_css_selector('a.ltkmodal-close')
    driver.execute_script("arguments[0].click();", element)

    all_store_data = []
    coords = driver.execute_script('return markersCoords')

    for loc in coords:
        html_cont = loc['address'].replace('&lt;', '<').replace('&quot;', '"').replace('&gt;', '>').replace('&#039;',
                                                                                                            '"')
        soup = BeautifulSoup(html_cont, 'html.parser')

        location_name = soup.find('span', {'class': 'name'}).text.strip()
        street_address = soup.find('span', {'class': 'address'}).text.strip()
        city = soup.find('span', {'class': 'city'}).text.strip()
        state = soup.find('span', {'class': 'prov_state'}).text.strip()
        zip_code = soup.find('span', {'class': 'postal_zip'}).text.strip()
        if len(zip_code.split(' ')) == 1:
            zip_code = '<MISSING>'

        country_code = 'CA'
        hours = soup.find('span', {'class': 'hours'}).text.replace('PM', 'PM ')
        hours = ' '.join(hours.split())
        phone_number = soup.find('span', {'class': 'phone'}).text.strip()

        lat = loc['lat']
        longit = loc['lng']

        location_type = '<MISSING>'
        page_url = '<MISSING>'

        store_number = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
