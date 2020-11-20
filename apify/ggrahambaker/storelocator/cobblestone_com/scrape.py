import csv
from sgselenium import SgChrome
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

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
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://cobblestone.com/'
    ext = 'locations/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    driver = SgChrome().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []
    div = driver.find_element_by_css_selector('div#results')
    locations = div.find_elements_by_css_selector('div.result')
    for loc in locations:
        link = loc.find_element_by_css_selector('.result_website>a').get_attribute('href')
        line_split = loc.text.split('\n')
        location_name = line_split[0][:-10]
        street_address = line_split[1]
        city, state, zip_code = addy_ext(line_split[2])        
        href_link = loc.find_element_by_css_selector('a.result_directions').get_attribute('href')
        start_idx = href_link.find('&daddr')
        end_idx = href_link.find('(')
        coords = href_link[start_idx + 7:end_idx].split(',')
        lat = coords[0]
        longit = coords[1]
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<INACCESSIBLE>'
        phone_number = line_split[3].replace('Phone:', '').strip()
        if "-" not in phone_number:
            req = session.get(link, headers = HEADERS)
            base = BeautifulSoup(req.text,"lxml")
            phone_number = base.find(class_="location__description").find_all("a")[-1].text

        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
