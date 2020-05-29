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
    locator_domain = 'https://verlo.com/'
    url = 'https://code.metalocator.com/index.php?option=com_locator&view=directory&layout=combined&Itemid=11493&tmpl=component&framed=1&source=js'

    driver = SgSelenium().chrome()
    driver.get(url)
    all_store_data = []
    locs = driver.find_elements_by_css_selector('div.com_locator_entry')

    for loc in locs:
        location_name = loc.find_element_by_css_selector('h2').find_element_by_css_selector('a').text

        street_address = loc.find_element_by_css_selector('span.address').text
        city = loc.find_element_by_css_selector('span.city').text
        state = loc.find_element_by_css_selector('span.state').text
        zip_code = loc.find_element_by_css_selector('span.postalcode').text
        
        phone_number = loc.find_element_by_css_selector('span.phone').text
        
        try:
            hours = ''
            days = loc.find_element_by_css_selector('tbody').find_elements_by_css_selector('tr')

            for day in days:
                day_of_week = day.find_element_by_css_selector('td.ml_weekdayname').text
                start = day.find_element_by_css_selector('td.ml_hours_opening').text
                end = day.find_element_by_css_selector('td.ml_hours_closing').text
                
                hours += day_of_week + ' ' + start + ' - ' + end + ' '
        except NoSuchElementException:
            hours = '<MISSING>'
    
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = loc.find_element_by_css_selector('span.link').find_element_by_css_selector('a').get_attribute('href')

        longit = '<MISSING>'
        lat = '<MISSING>'
        store_number = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
