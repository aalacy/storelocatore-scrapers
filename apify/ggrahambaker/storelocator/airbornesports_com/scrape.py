import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://airbornesports.com/'
    ext = 'hours-and-pricing/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    section = driver.find_element_by_css_selector('section#content')
    buttons = section.find_elements_by_css_selector('a.fusion-button.button-flat.fusion-button-round')
    link_list = []
    for button in buttons:
        href = button.get_attribute('href')
        if href not in link_list:
            link_list.append(href)

    carry_on_list = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        hours = driver.find_element_by_css_selector('div.reading-box-additional').text.replace('\n', ' ')

        try:
            href = driver.find_element_by_xpath("//a[contains(@href, 'google')]").get_attribute('href')

            start_idx = href.find('/@')
            end_idx = href.find('z/data')

            coords = href[start_idx + 2: end_idx].split(',')

            lat = coords[0]
            longit = coords[1]

        except NoSuchElementException:
            lat = '<MISSING>'
            longit = '<MISSING>'

        phone_number = driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").get_attribute('href').replace(
            'tel:+1', '')

        span = driver.find_element_by_xpath("//span[contains(text(),'WAIVER')]")
        href_waiv = span.find_element_by_xpath('..').get_attribute('href')

        carry_on_list.append([href_waiv, hours, lat, longit, phone_number])

    all_store_data = []
    for store in carry_on_list:
        driver.get(store[0])
        driver.implicitly_wait(15)

        foot = driver.find_element_by_css_selector('footer#page_footer')
        location_name = foot.find_element_by_css_selector('p.business-name').text

        addy = driver.find_element_by_css_selector('p.business-address.nobreak').text

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

        hours = store[1]
        lat = store[2]
        longit = store[3]
        phone_number = store[4]
        country_code = 'US'
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
