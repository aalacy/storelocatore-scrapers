import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json



def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.johnnyrockets.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    element = driver.find_element_by_css_selector('div#show_all_locs')
    driver.execute_script("arguments[0].click();", element)

    usa = driver.find_element_by_css_selector('div#cg_usa')

    hrefs = usa.find_elements_by_xpath("//a[contains(@href, '/locations/')]")



    link_list = []
    for href in hrefs:
        link = href.get_attribute('href')
        if 'emporium-fortitude-valley-brisbane-australia' in link:
            break

        if len(link) > 45:
            link_list.append(link)

    all_store_data = []
    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_css_selector('div.data__title').text

        loc_j = driver.find_elements_by_xpath('//script[@type="application/ld+json"]')
        loc_json = json.loads(loc_j[1].get_attribute('innerHTML'))

        addy = loc_json['address']
        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']

        zip_code = addy['postalCode']
        if zip_code == '':
            zip_code = '<MISSING>'


        if 'openingHours' in loc_json:
            hours = ''
            hours_list = loc_json['openingHours']
            for h in hours_list:
                hours += h + ' '

            hours = hours.strip()
        else:
            hours = '<MISSING>'


        if 'telephone' in loc_json:
            phone_number = loc_json['telephone']
        else:
            phone_number = '<MISSING>'


        geo = driver.find_element_by_css_selector('div.list__item.loc_item')
        lat = geo.get_attribute('data-lat')
        longit = geo.get_attribute('data-lon')

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'US'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
