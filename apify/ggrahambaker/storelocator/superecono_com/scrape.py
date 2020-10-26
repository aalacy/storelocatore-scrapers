import csv
import os
from sgselenium import SgSelenium
from postal.parser import parse_address

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://superecono.com/'
    ext = 'tiendas'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    stores = driver.find_elements_by_css_selector('div.listerItem')
    link_list = []
    for store in stores:
        link_list.append(store.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        print(link)

        driver.get(link)
        driver.implicitly_wait(10)

        cont = driver.find_element_by_css_selector('div.container.main-content').text.split('\n')
        location_name = cont[0]
        start_idx = cont.index('Horario de Operación')
        content = cont[start_idx:]
        hours = content[2] + ' ' + content[3]
        raw_address = content[4]
        phone_number = content[-1]
        parsed_address = parse_address(raw_address)
        city_opt = [x[0] for x in parsed_address if x[1] == 'city']
        city = city_opt[0] if len(city_opt) > 0 else '<MISSING>'
        zip_code_opt = [x[0] for x in parsed_address if x[1] == 'postcode']
        zip_code = zip_code_opt[0] if len(zip_code_opt) > 0 else '<MISSING>'
        number_opt = [x[0] for x in parsed_address if x[1] == 'house_number']
        number = number_opt[0] if len(number_opt) > 0 else ''
        name = [x[0] for x in parsed_address if x[1] == 'road'][0]
        street_address = ' '.join([x for x in [number, name] if x])
        state = 'PR'

        src = driver.find_elements_by_css_selector('iframe')
        if len(src) == 1:
            src = driver.find_element_by_css_selector('iframe').get_attribute('src')

            start = src.find('!2d')
            end = src.find('!3m2')

            if start > 1:
                coords = src[start + 3: end].split('!3d')
                lat = coords[1][:9]
                longit = coords[0][:8]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

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
