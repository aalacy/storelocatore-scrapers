import csv
import os
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('batterygiant_com')



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
    locator_domain = 'https://www.batterygiant.com/'
    ext = 'store-locator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    tds = driver.find_elements_by_css_selector('td.storeLink')
    link_list = []
    for td in tds:
        link_list.append(td.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        cont = driver.find_element_by_css_selector('div.grid_92')
        content = cont.text.split('\n')

        if 'Panama' in content[0]:
            continue
        #logger.info(len(content))
        #logger.info(content)
        if len(content) == 13:
            street_address = content[3]
            city, state, zip_code = addy_ext(content[4])
            phone_number = content[6]
            hours = ''
            for h in content[10:]:
                hours += h + ' '
            hours = hours.strip()

        elif len(content) == 16:
            if 'Louisville' in content[0] :
                street_address = content[5]
                city, state, zip_code = addy_ext(content[6])
                phone_number = content[8]
            elif 'Downers Grove' in content[0]:
                street_address = content[4]
                city, state, zip_code = addy_ext(content[5])
                phone_number = content[7]
            else:
                street_address = content[6]
                city, state, zip_code = addy_ext(content[7])
                phone_number = content[9]

            hours = ''
            for h in content[13:]:
                hours += h + ' '
            hours = hours.strip()
        elif len(content) < 11:
            if len(content) == 9:
                street_address = content[2] + ' ' + content[3]

                city, state, zip_code = addy_ext(content[4])
                phone_number = content[6]
                hours = '<MISSING>'

            else:
                street_address = content[2]
                city, state, zip_code = addy_ext(content[3])

                phone_number = content[5]
                hours = ''
                for h in content[7:]:
                    hours += h + ' '
                hours = hours.strip()

        location_name = '<MISSING>'
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
