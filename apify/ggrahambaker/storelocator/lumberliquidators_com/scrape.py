import csv
import os
from sgselenium import SgSelenium
import usaddress
from selenium.common.exceptions import NoSuchElementException
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lumberliquidators_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def can_addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1] + ' ' + state_zip[2]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.lumberliquidators.com/'
    ext = 'll/stores/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    #main = driver.find_element_by_css_selector('ul.Directory-listLinks')
    state_links = driver.find_elements_by_css_selector('a.Directory-listLink')

    # store_link
    state_link_list = []
    store_link_list = []

    for state_link in state_links:
        href = state_link.get_attribute('href')
        if len(href) > 46:
            store_link_list.append(href)
        else:
            state_link_list.append(href)

    for state_link in state_link_list:
        driver.get(state_link)
        driver.implicitly_wait(10)

        main = driver.find_element_by_css_selector('ul.Directory-listLinks')
        store_links = main.find_elements_by_css_selector('a.Directory-listLink')
        for store in store_links:
            store_link_list.append(store.get_attribute('href'))

    ## canada locs
    driver.get('http://www.lumberliquidators.ca/can/storelocator/toronto')
    driver.implicitly_wait(10)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'ON-')]")

    for h in hrefs:
        store_link_list.append(h.get_attribute('href'))

    all_store_data = []
    for i, link in enumerate(store_link_list):
        driver.get(link)
        driver.implicitly_wait(10)
        logger.info(link)
        logger.info(i)

        try:
            location_name = driver.find_element_by_css_selector('h1#location-name').text.replace('\n', ' ')
        except NoSuchElementException:
            ## more locations
            logger.info('')
            logger.info('')
            logger.info('more locs!')
            store_links = driver.find_elements_by_css_selector('a.Teaser-titleLink')
            for store in store_links:
                logger.info(store.get_attribute('href'))
                store_link_list.append(store.get_attribute('href'))

            continue

        logger.info(location_name)

        if 'ON-' in link:
            country_code = 'CA'
            addy = driver.find_element_by_css_selector('div.Core-address').text.split('\n')
            logger.info(addy)
            street_address = addy[0]
            city, state, zip_code = can_addy_ext(addy[1])

        else:
            country_code = 'US'

            addy = driver.find_element_by_css_selector('div.Core-address').text.replace('\n', ' ')
            logger.info(addy)

            if '2465 Highway 6 and 50' in addy:
                street_address = '2465 Highway 6 and 50'
                city = 'Grand Junction'
                state = 'CO'
                zip_code = '81505'
            elif '110 Water Tower Plaza' in addy:
                street_address = '110 Water Tower Plaza'
                city = 'Leominster'
                state = 'MA'
                zip_code = '01453'
            else:

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
                city = parsed_add['PlaceName']
                state = parsed_add['StateName']
                zip_code = parsed_add['ZipCode']

        logger.info(street_address, city, state, zip_code)

        phone_number = driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").get_attribute('href').replace(
            'tel:', '')

        logger.info(phone_number)
        hours = driver.find_element_by_css_selector('table.c-location-hours-details').text.replace('\n', ' ').replace(
            'Day of the Week', '').strip()
        logger.info(hours)

        lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')
        logger.info(longit, lat)
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
