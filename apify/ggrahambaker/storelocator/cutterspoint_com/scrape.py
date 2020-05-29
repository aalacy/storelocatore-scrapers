import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0].strip()
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.cutterspoint.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_css_selector('a.cpStore')

    link_list = []
    for href in hrefs:
        link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.implicitly_wait(10)
        driver.get(link)
        container = driver.find_element_by_css_selector('div#slide2').find_element_by_css_selector('div.span6')

        ps = container.find_elements_by_css_selector('p')

        address = ps[0].text.split('\n')
        street_address = address[0]
        city, state, zip_code = addy_ext(address[1])

        href = ps[0].find_element_by_css_selector('a').get_attribute('href')
        start_idx = href.find('q=')

        coords = href[start_idx + 2:].split(',')
        lat = coords[0]
        longit = coords[1]

        phone_number = ps[1].text

        types = ps[2].find_elements_by_css_selector('img')
        sit_down = False
        drive_through = False
        for t in types:
            if 'sit' in t.get_attribute('src'):
                sit_down = True
            else:
                drive_through = True

        location_type = ''
        if drive_through:
            location_type += 'Drive Through '
        if sit_down:
            location_type += 'Sit Down '

        location_type = location_type.strip()

        ## hours
        days = container.find_elements_by_css_selector('div.hrsTitle')
        times = container.find_elements_by_css_selector('div.hrsTime')

        hours = ''
        for i, h in enumerate(days):
            hours += days[i].text + ' ' + times[i].text + ' '

        country_code = 'US'
        location_name = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
