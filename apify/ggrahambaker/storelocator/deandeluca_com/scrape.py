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

def fetch_data():
    locator_domain = 'https://www.deandeluca.com/'
    ext = 'new-page-1'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    main = driver.find_element_by_css_selector('div#page-5d1254918618110001ee3953')
    locs = main.find_elements_by_css_selector('div.row.sqs-row')
    done = False
    all_store_data = []
    for loc in locs:
        content = loc.text.split('\n')

        country_code = 'US'
        store_number = '<MISSING>'

        lat = '<MISSING>'
        longit = '<MISSING>'
        if not done:
            if len(content) == 5:
                location_name = content[0]
                location_type = content[1]
                phone_number = content[2]
                address = content[3].split(',')
                street_address = address[0]
                city = address[1].strip()
                state_zip = address[2].strip().split(' ')
                state = state_zip[0]
                zip_code = state_zip[1]
                hours = content[4]

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)
            else:
                ny_times = content[0:5]

                location_name = ny_times[0]
                location_type = ny_times[1]
                phone_number = ny_times[2]
                address = ny_times[3].split(',')
                street_address = address[0]
                city = address[1].strip()
                state_zip = address[2].strip().split(' ')
                state = state_zip[0]
                zip_code = state_zip[1]
                hours = ny_times[4]
                ## done
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

                hours = '<MISSING>'
                hi_mark = content[5:9]

                phone_number = hi_mark[0]
                address = hi_mark[1].split(',')
                street_address = address[0]
                city = address[1].strip()
                state_zip = address[2].strip().split(' ')
                state = state_zip[0]
                zip_code = state_zip[1]
                location_name = hi_mark[2] + ' ' + hi_mark[3]
                location_type = hi_mark[3]

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

                hi_cafe = content[9:]

                phone_number = hi_cafe[0]
                address = hi_cafe[2].split(',')
                street_address = address[0] + ' ' + address[1] + ' ' + address[2]
                city = address[3].strip()
                state_zip = address[4].strip().split(' ')
                state = state_zip[0]
                zip_code = state_zip[1]
                location_name = hi_cafe[3] + ' ' + hi_cafe[4]
                location_type = hi_cafe[4]

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)
                done = True

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
