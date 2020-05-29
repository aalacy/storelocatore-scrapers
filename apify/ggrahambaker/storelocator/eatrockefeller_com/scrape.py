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
    locator_domain = 'https://www.eatrockefeller.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    id_arr = ['#mediaisfplg6i2inlineContent-gridWrapper', '#mediaisfplg6h1inlineContent-gridWrapper',
              '#comp-jep6p29rinlineContent-gridWrapper']
    all_store_data = []
    for id_tag in id_arr:
        content = driver.find_element_by_css_selector('div' + id_tag).text.split('\n')

        if len(content) == 12:
            location_name = content[1]
            phone_number = content[2]
            street_address = content[3]
            city, state, zip_code = addy_ext(content[4])
            hours = ''
            for h in content[5:]:
                hours += h + ' '

            hours = hours.strip()
        else:
            location_name = content[0]
            phone_number = content[1]
            street_address = content[2]
            city, state, zip_code = addy_ext(content[3])
            hours = ''
            for h in content[4:-1]:
                hours += h + ' '

            hours = hours.strip()


        lat = '<INACCESSIBLE>'
        longit = '<INACCESSIBLE>'
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
