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
    if len(address) == 1:
        address = addy.split(' ')
        if len(address) == 4:
            city = address[0] + ' ' + address[1]
            state = address[2]
            zip_code = address[3]
        else:
            city = address[0]
            state = address[1]
            zip_code = address[2]
    else:
        city = address[0]
        state_zip = address[1].strip().split(' ')
        if len(state_zip) == 3:
            state = state_zip[0] + ' ' + state_zip[1]
            zip_code = state_zip[2]
        else:
            state = state_zip[0].strip()
            zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://gatorsdockside.com/'
    ext = 'restaurants/locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    hrefs = driver.find_elements_by_css_selector('a.details')

    link_list = [href.get_attribute('href') for href in hrefs]

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        content = driver.find_element_by_css_selector('div.entry-content').text.split('\n')

        if len(content) == 11:
            content = content[:-5]
        elif len(content) == 12:
            content = content[:-6]
        elif len(content) == 10:
            content = content[:-5]
        elif len(content) == 13:
            content = content[:-6]
        if 'HUNTER' in content[0]:
            content = content[:-1]
        elif 'OCALA' in content[0]:
            content = content[:-1]
        elif 'CANAVERAL' in content[0]:
            content = content[:-1]
        elif 'CLOUD' in content[0]:
            content = content[:-1]
        elif 'TAMPA' in content[0]:
            content = content[:-1]

        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[3]
        hours = ''
        for h in content[4:]:
            hours += h + ' '

        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
