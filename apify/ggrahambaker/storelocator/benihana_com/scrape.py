import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import usaddress
import re

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
    locator_domain = 'https://www.benihana.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div#locations')
    locs = main.find_elements_by_css_selector('div.one_third')

    link_list = []
    for loc in locs:
        if 'Delivery' in loc.find_element_by_css_selector('div.location-address').text:
            continue

        href = loc.find_element_by_css_selector('div.location-link').find_element_by_css_selector('a').get_attribute(
            'href')
        if 'palmbeach-aw-pa' in href:
            break

        link_list.append(href)

    all_store_data = []
    for link in link_list:
        print(link)
        driver.get(link)
        driver.implicitly_wait(60)

        if 'talking-stick-resort-arena-az/' in link:
            location_name = 'Talking Stick Resort Arena, AZ'
            addy = '201 E Jefferson St, Phoenix, AZ 85004'
            street_address = '201 E Jefferson St'
            city = 'Phoenix'
            state = 'AZ'
            zip_code = '85004'
            hours = '<MISSING>'
            phone_number = '<MISSING>'
            location_type = 'Stadium'
        else:
            try:
                location_name = driver.find_element_by_css_selector('h2.ppb_title').text
            except NoSuchElementException:
                try:
                    location_name = driver.find_element_by_css_selector('h3.ppb_title').text
                except NoSuchElementException:
                    print(link)


            if '18400 Avalon Blvd., Carson, CA 90746' in driver.find_element_by_css_selector('div.location-snippet').text:
                addy = '18400 Avalon Blvd., Carson, CA 90746'
            elif '347 Don Shula Dr., Miami Gardens, FL 33056' in driver.find_element_by_css_selector('div.location-snippet').text:
                addy = '347 Don Shula Dr., Miami Gardens, FL 33056'
            elif '1407 Grand Blvd., Kansas City, MO 64106' in driver.find_element_by_css_selector('div.location-snippet').text:
                addy = '1407 Grand Blvd., Kansas City, MO 64106'
            elif '1 E 161 St, The Bronx, NY 10451' in driver.find_element_by_css_selector('div.location-snippet').text:
                addy = '1 E 161 St, The Bronx, NY 10451'

            elif '1665 NE 79th Street Causeway' in driver.find_element_by_css_selector('div.location-snippet').text:
                #not open yet
                continue
            else:

                loc_snip = driver.find_elements_by_css_selector('div.location-snippet')
                if len(loc_snip) == 1:
                    addy = loc_snip[0].find_element_by_css_selector('.address').text
                else:
                    addy = loc_snip[1].find_element_by_css_selector('.address').text


            zip_re = re.compile('[A-Z][A-Z]\ \d{5}')

            for m in zip_re.finditer(addy):
                addy = addy[:m.end()]



            parsed_add = usaddress.tag(addy)[0]

            street_address = ''

            if 'AddressNumber' in parsed_add:
                street_address += parsed_add['AddressNumber'] + ' '
            if 'StreetNamePreDirectional' in parsed_add:
                street_address += parsed_add['StreetNamePreDirectional'] + ' '
            if 'StreetName' in parsed_add:
                street_address += parsed_add['StreetName'] + ' '
            if 'StreetNamePostType' in parsed_add:
                street_address += parsed_add['StreetNamePostType'] + ' '
            if 'OccupancyType' in parsed_add:
                street_address += parsed_add['OccupancyType'] + ' '
            if 'OccupancyIdentifier' in parsed_add:
                street_address += parsed_add['OccupancyIdentifier'] + ' '

            street_address = street_address.replace('\n', '').strip()
            city = parsed_add['PlaceName']
            state = parsed_add['StateName']
            zip_code = parsed_add['ZipCode']

            main_cont = driver.find_element_by_css_selector('div.inner')

            try:
                phone_number = main_cont.find_element_by_xpath('//span[@itemprop="telephone"]').text
                hours = main_cont.find_element_by_css_selector('div.hours-wrapper').text.replace('\n', ' ')
                location_type = '<MISSING>'
            except NoSuchElementException:
                hours = '<MISSING>'
                phone_number = '<MISSING>'
                location_type = 'Stadium'

        country_code = 'US'
        store_number = '<MISSING>'

        longit = '<MISSING>'
        lat = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
