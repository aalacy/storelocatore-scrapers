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
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://www.cruisincoffee.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    div = driver.find_element_by_css_selector('div.entry.clearfix')
    ps = div.find_elements_by_css_selector('p')
    all_store_data = []
    count = 0
    for i, p in enumerate(ps[2:]):
        if p.text == '':
            if count != 0:
                country_code = 'US'
                store_number = '<MISSING>'
                location_type = '<MISSING>'
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)
            count = 0
            continue
        if (count % 6) == 0:
            location_name = p.text.strip()
        elif (count % 6) == 1:
            ##address & phonenumber & coords
            address = p.text.split('\n')
            street_address = address[0]
            city, state, zip_code = addy_ext(address[1])
            phone_number = address[2].replace('Phone:', '').strip()

            href = p.find_element_by_css_selector('a').get_attribute('href')
            start_idx = href.find('&sll=')
            end_idx = href.find('&ssp')

            coords = href[start_idx + 5: end_idx].split(',')
            lat = coords[0]
            longit = coords[1]
        elif (count % 6) == 3:
            ##address & phonenumber
            hours = ''
            hours_arr = p.text.split('\n')
            for h in hours_arr:
                if 'Cruisin Coffee is open' in h:
                    continue
                else:
                    hours += h + ' '

            if '111 E. Washington St' in street_address:
                country_code = 'US'
                store_number = '<MISSING>'
                location_type = '<MISSING>'
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)
        count += 1

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
