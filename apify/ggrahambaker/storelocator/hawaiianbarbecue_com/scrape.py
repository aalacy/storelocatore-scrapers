import csv
import os
from sgselenium import SgSelenium
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hawaiianbarbecue_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.hawaiianbarbecue.com/'
    ext = 'locations-list/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    time.sleep(4)
    driver.implicitly_wait(30)

    close = driver.find_element_by_css_selector('div.mailer__close')
    driver.execute_script("arguments[0].click();", close)

    cities = driver.find_elements_by_css_selector('li.location')
    link_list = []
    for city in cities:
        link = city.find_element_by_css_selector('a').get_attribute('href')
        if link in link_list:
            continue
        else:
            link_list.append(link)

    all_store_data = []
    dup_tracker = []
    for link in link_list:
        logger.info(link)
        if 'undefined' in link:
            continue

        driver.get(link)

        time.sleep(4)
        driver.implicitly_wait(30)
        location_name = driver.find_element_by_css_selector('h5.location-detail__location-name').text
        
        if 'COMING SOON' in location_name:
            continue
        if 'Closed' in location_name:
            continue
        
        if location_name not in dup_tracker:
            dup_tracker.append(location_name)
        else:
            continue

        street_address = driver.find_element_by_css_selector('li.location-detail__address-line-1').text
        city = driver.find_element_by_css_selector('li.location-detail__locality').text
        state = driver.find_element_by_css_selector('span.state').text
        if 'Japan' in state:
            break
        zip_code = driver.find_element_by_css_selector('span.zip').text
        
        phone_number = driver.find_element_by_css_selector('li.location-detail__phone').text
        if phone_number == '':
            phone_number = '<MISSING>'

        hours = driver.find_element_by_css_selector('div.location-detail__hours').text.replace('\n', ' ').strip()
        if hours == '':
            hours = '<MISSING>'
        google_href = driver.find_element_by_xpath("//a[contains(@href, 'maps.google.com/maps')]").get_attribute('href')

        start = google_href.find('?ll=')
        if start > 0:
            end = google_href.find('&z=')
            coords = google_href[start + 4: end].split(',')
            lat = coords[0]
            longit = coords[1]
            
        country_code = 'US'
        page_url = link
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
