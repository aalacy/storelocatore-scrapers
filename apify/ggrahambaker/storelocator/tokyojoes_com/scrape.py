import csv
import os
from sgselenium import SgSelenium
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://tokyojoes.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'order.tokyojoes.com/menu')]")
    link_list = []
    for h in hrefs:
        link_list.append(h.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_css_selector('div.fn.org').find_element_by_css_selector('h1').text

        street_address = driver.find_element_by_css_selector('span.street-address').text
        city = driver.find_element_by_css_selector('span.locality').text
        state = driver.find_element_by_css_selector('span.region').text
        zip_code = driver.find_element_by_css_selector('span.postal-code').text

        lat = driver.find_element_by_css_selector('span.latitude').find_element_by_css_selector('span').get_attribute(
            'title')
        longit = driver.find_element_by_css_selector('span.longitude').find_element_by_css_selector(
            'span').get_attribute('title')

        phone_number = driver.find_element_by_css_selector('span.tel').text

        hours_html = driver.find_element_by_xpath('//div[@id="business-sched-tmpl"]').get_attribute('innerHTML')

        hours = BeautifulSoup(hours_html, 'html.parser').text.replace('Business Hours', '').replace('\n', ' ').strip()

        country_code = 'US'

        location_type = '<MISSING>'
        page_url = link
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
