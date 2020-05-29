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


def cut(arr):
    for i, a in enumerate(arr):
        if 'Hours' in a:
            return i





def fetch_data():
    locator_domain = 'http://www.tasteofphilly.biz/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    stores = driver.find_elements_by_css_selector('div.top-menu-lr')
    link_list = []
    for store in stores:
        link_list.append(store.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        if 'famous' in link:
            continue

        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('div.top-menu-lr').text.split('\n')

        location_name = driver.find_element_by_css_selector('h1.post-title').text

        if len(main) == 1:
            content = driver.find_element_by_css_selector('div.post-entry').text.split('\n')

            street_address = content[0]
            city, state, zip_code = addy_ext(content[1])
            phone_number = content[2]
            hours = content[6]

            src = driver.find_element_by_css_selector('iframe').get_attribute('src')
            start = src.find('&sll=')
            end = src.find('&ssp')
            if start > 1:
                coords = src[start + 5: end].split(',')
                lat = coords[0]
                longit = coords[1]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'

        elif len(main) == 6:
            phone_number = main[3]
            addy = main[4].split('.')
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1].strip())

            src = driver.find_element_by_css_selector('iframe').get_attribute('src')

            start = src.find('!2d')
            end = src.find('!3m2')
            if start > 1:
                coords = src[start + 3: end].split('!3d')
                lat = coords[1][:10]
                longit = coords[0][:10]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'

            hours = '<MISSING>'

        else:
            street_address = main[0]
            city, state, zip_code = addy_ext(main[1])

            phone_number = main[2]
            hours_idx = cut(main) + 1
            hours = ''
            for h in main[hours_idx:]:
                if ':' in h or '-' in h:
                    if 'Free' not in h and 'Delivery' not in h:
                        hours += h + ' '

            src = driver.find_element_by_css_selector('iframe').get_attribute('src')

            start = src.find('&sll=')
            end = src.find('&ssp')
            if start > 1:
                coords = src[start + 5: end].split(',')
                lat = coords[0]
                longit = coords[1]
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
