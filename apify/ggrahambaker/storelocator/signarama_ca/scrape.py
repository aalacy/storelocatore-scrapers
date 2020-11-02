import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.signarama.ca'
    ext = '/storelocator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.state_stors')
    hrefs = main.find_elements_by_css_selector('a')

    link_list = []
    for href in hrefs:
        link = href.get_attribute('href')
        if 'signaramafranchise' in link:
            continue

        link_list.append(link)

    all_store_data = []

    duplicate_tracker = []
    for i, link in enumerate(link_list):

        driver.get(link)
        driver.implicitly_wait(10)

        start_idx = link.find('.ca/') + 4

        location_name = link[start_idx:].replace('-', ' ')

        try:
            foot = driver.find_element_by_css_selector('div.aboutsignarama-ft')
            addy = foot.find_element_by_css_selector('address').text.split(',')
            street_address = addy[0].strip()
            if len(addy) > 4:
                street_address += addy[1].strip()
                city = addy[2].strip()
                state = addy[3].strip()
                canada_zip = addy[4].split('-')
                zip_code = canada_zip[1].strip()
            elif len(addy) == 2:
                ['4308 Village Centre Ct\nMississauga', ' Ontario L4Z-1S2']

                street_add = addy[0].split('\n')
                street_address = street_add[0]
                city = street_add[1]

                state_zip = addy[1].strip().split(' ')
                state = state_zip[0]
                zip_code = state_zip[1]
            else:
                city = addy[1].strip()
                filt = ''.join(c for c in city if c.isdigit())
                if len(filt) > 0:
                    zip_code = city
                    state = addy[2].strip()
                    canada_city = addy[3].split('-')
                    city = canada_city[1].strip()

                else:
                    state = addy[2].strip()
                    canada_zip = addy[3].split('-')
                    zip_code = canada_zip[1].strip()

            phone_number_a = driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").get_attribute('href')
            phone_number = phone_number_a.replace('tel:', '')

            try:
                href = driver.find_element_by_xpath("//a[contains(@href, 'maps.google.com')]").get_attribute('href')

                start_idx = href.find('?ll=')
                end_idx = href.find('&z=')
                coords = href[start_idx + 4: end_idx].split(',')
                lat = coords[0]
                longit = coords[1]

            except NoSuchElementException:

                lat = '<MISSING>'
                longit = '<MISSING>'

        except NoSuchElementException:
            # different site
            phone_number = driver.find_element_by_css_selector('h3.widget-title').text

            addy = driver.find_element_by_css_selector('div.carte-caption').text.split('\n')
            location_name = addy[0]

            addy_split = addy[1].split(',')

            if len(addy_split) == 4:
                if '328 F' in addy_split[0]:
                    street_address = addy_split[0] + addy_split[1]
                    city = addy_split[2].strip()
                    state = 'QC'
                    zip_code = addy_split[3].strip()
                else:
                    street_address = addy_split[0]
                    city = addy_split[1].strip()
                    state = addy_split[2].strip()
                    zip_code = addy_split[3].strip()

            elif len(addy_split) == 3:
                street_address = addy_split[0]
                city = addy_split[1].strip()
                state = 'QC'
                zip_code = addy_split[2].strip()
            else:
                street_address = addy_split[0] + addy_split[1]
                city = addy_split[2].strip()
                state = addy_split[3].strip()
                zip_code = addy_split[4].strip()

            lat = '<MISSING>'
            longit = '<MISSING>'

            src = driver.find_element_by_xpath("//iframe[contains(@src, 'www.google.com/maps/')]").get_attribute('src')
            start = src.find('!2d')
            if start > 0:
                end = src.find('!3m')
                
                coords = src[start + 3: end].split('!3d')
                lat = coords[1].split('!2m')[0]
                longit = coords[0]
            
        if street_address not in duplicate_tracker:
            duplicate_tracker.append(street_address)
        else:
            continue

        zip_code = zip_code.replace('-', ' ')
        if len(zip_code.split(' ')) == 3:
            zip_code_ar = zip_code.split(' ')
            zip_code = zip_code_ar[1] + ' ' + zip_code_ar[2]

        country_code = 'CA'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'
        page_url = link
        phone_number = phone_number.replace('+', '').strip()

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
