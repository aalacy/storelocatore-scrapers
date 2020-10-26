import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoAlertPresentException
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('xsportfitness_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    if len(address) == 1:
        addy = address[0].split(' ')
        city = addy[0]
        state = addy[1]
        zip_code = addy[2]
    else:
        city = address[0]
        state_zip = address[1].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.xsportfitness.com/'
    ext = 'locations/index.aspx'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(30)

    while True:
        try:
            alert_obj = driver.switch_to.alert
            alert_obj.accept()
            break

        except NoAlertPresentException:
            time.sleep(5)

    locs = driver.find_element_by_css_selector('ul.list').find_elements_by_css_selector('li')
    link_list = []
    for l in locs:
        loc_link = l.find_element_by_css_selector('a').get_attribute('href')
        link_list.append(loc_link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        main = driver.find_element_by_css_selector('main#maincontent')

        sub_main = main.find_element_by_css_selector('div.callout.large.row')

        cont = sub_main.find_element_by_css_selector('div.large-3.columns')
        location_name = cont.find_element_by_css_selector('h1').text.split('\n')[0]

        addy_and_phone = cont.find_elements_by_css_selector('p')

        addy = addy_and_phone[0].text.split('\n')

        if len(addy) == 3:
            if 'In the' in addy[0]:
                street_address = addy[1]
            else:
                street_address = addy[0] + ' ' + addy[1]
            city, state, zip_code = addy_ext(addy[2])

        else:
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1])

        phone_number = addy_and_phone[1].text

        hours = cont.find_element_by_css_selector('h5').text

        if 'OPEN 24/7' not in hours:
            hours = addy_and_phone[2].text.replace('\n', ' ')

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        longit = '<MISSING>'
        lat = '<MISSING>'

        page_url = link

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        logger.info()
        logger.info(store_data)
        logger.info()
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
