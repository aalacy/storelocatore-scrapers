import csv
import os
from sgselenium import SgSelenium
from sgrequests import SgRequests
from bs4 import BeautifulSoup


session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.figandolive.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    element = driver.find_element_by_css_selector('li.site-nav-submenu').find_element_by_css_selector('button')
    driver.execute_script("arguments[0].click();", element)

    lis = driver.find_element_by_css_selector('div#SubMenu-1').find_elements_by_css_selector('li')
    link_list = []
    for li in lis:
        link_list.append(li.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []

    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        start_idx = link.find('-olive')

        location_name = link[start_idx + 7:-1].replace('-', ' ')
        phone_number = driver.find_element_by_xpath('//a[@data-bb-track-category="Phone Number"]').get_attribute(
            'href').replace('tel:', '')
        address = driver.find_element_by_css_selector('div.gmaps').get_attribute('data-gmaps-address').split(',')
        page = session.get(link)
        assert page.status_code == 200

        soup = BeautifulSoup(page.content, 'html.parser')
        main = soup.find('section', {'id': 'intro'})
        ps = main.find_all('p')

        hours = ''
        for i, p in enumerate(ps):
            if '00pm' in p.text or '00am' in p.text:
                hours += p.text + ' '


        hours = hours.strip()
        if len(address) == 4:
            street_address = address[1]
            city = address[2].strip()
            state_zip = address[3].strip().split(' ')

            state = state_zip[0]
            zip_code = state_zip[1]
        else:
            street_address = address[0]
            city = address[1].strip()
            state_zip = address[2].strip().split(' ')

            state = state_zip[0]
            zip_code = state_zip[1]

        lat = driver.find_element_by_css_selector('div.gmaps').get_attribute('data-gmaps-lat')
        longit = driver.find_element_by_css_selector('div.gmaps').get_attribute('data-gmaps-lng')

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
