import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('zehrs_ca')



options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument(
    "user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)
#driver3 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver3 = webdriver.Chrome("chromedriver", options=options)


def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    if len(state_zip) == 4:
        logger.info('four!!')
    else:
        state = state_zip[0]
        zip_code = state_zip[1] + ' ' + state_zip[2]
    return city, state, zip_code


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    data = []
    driver.get("https://www.zehrs.ca/store-locator?icta=store-locator")
    time.sleep(15)
    buttons = driver.find_elements_by_xpath("//button[@title='Zoom out']")
    for i in range(20):
        driver.execute_script("arguments[0].click();", buttons[0])
        time.sleep(1)
        buttons = driver.find_elements_by_xpath("//button[@title='Zoom out']")

    time.sleep(15)

    stores = driver.find_elements_by_css_selector(
        'a.location-list-item-actions__view-details__link')

    names = [stores[i].get_attribute("href") for i in range(0, len(stores))]

    for i in range(0, len(names)):
        driver2.get(names[i])
        time.sleep(5)
        page_url = names[i]
        store_opening_hours = driver2.find_element_by_css_selector(
            'ul.location-details-hours-content__list').text.replace('\n', ' ')

        phone_no = driver2.find_element_by_css_selector(
            'span.location-details-contact__contacts__item__value').text
        store_id = names[i].split("details/")[1]
        store_name = driver2.find_element_by_css_selector(
            'div.location-details-map__infobox__label').text

        street_address = driver2.find_element_by_css_selector(
            'div.location-address__line.location-address__line--line-1').text
        city, state, zip_code = addy_ext(driver2.find_element_by_css_selector(
            'div.location-address__line.location-address__line--region').text)
        data.append([
            'https://www.zehrs.ca/',
            page_url,
            store_name,
            street_address,
            city,
            state,
            zip_code,
            'CA',
            store_id,
            phone_no,
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            store_opening_hours
        ])

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
