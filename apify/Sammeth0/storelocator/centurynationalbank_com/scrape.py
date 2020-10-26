import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('centurynationalbank_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', options=options)


def fetch_data():
    pages_url = [];
    location_name = [];
    city = [];
    street_address = [];
    zipcode = [];
    ids = [];
    state = [];
    type = [];
    latitude = [];
    longitude = [];
    hours_of_operation = [];
    phone = []
    # Driver

    for i in range(1, 16):
        driver = get_driver()
        driver.get("https://centurynationalbank.com/locations/page/" + str(i)+"/?place&latitude&longitude&type=location")
        time.sleep(4)
        logger.info("https://centurynationalbank.com/locations/page/" + str(i)+"/?place&latitude&longitude&type=location")
        stores = driver.find_elements_by_xpath('/html/body/section[2]/section/div/div/div[1]/div')[1:]
        for s in stores:
            if "centurynationalbank.com" not in s.find_element_by_tag_name('a').get_attribute('href'):
                continue
            pages_url.append(s.find_element_by_tag_name('a').get_attribute('href'))
            logger.info(s.find_element_by_tag_name('a').get_attribute('href'))
            driver_page = get_driver()
            driver_page.get(s.find_element_by_tag_name('a').get_attribute('href'))
            time.sleep(4)
            location_name.append(driver_page.find_element_by_xpath('/html/body/section/section/div[1]/div[1]/h1').text+" "+driver_page.find_element_by_xpath("/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span[1]").text)
            #logger.info(location_name)
            try:
                street_address.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span[2]').text.split('\n')[0])
            except:
                street_address.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span').text.split('\n')[0])
            #logger.info(street_address)
            try:
                city.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span[2]').text.split('\n')[
                                1].split(',')[0])
            except:
                city.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span').text.split('\n')[1].split(
                    ',')[0])
            #logger.info(city)
            try:
                state.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span[2]').text.split('\n')[
                                 1].split(' ')[-2])
            except:
                state.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span').text.split('\n')[1].split(
                    ' ')[-2])
            #logger.info(state)
            try:
                zipcode.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span[2]').text.split('\n')[
                                   1].split(' ')[-1])
            except:
                zipcode.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span').text.split('\n')[1].split(
                    ' ')[-1])
            #logger.info(zipcode)
            ids.append(driver_page.find_element_by_xpath(
                '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[2]/div/a[2]').get_attribute(
                'data-locationid'))
            #logger.info(ids)
            try:
                phone.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span[2]').text.split('\n')[2])
            except:
                phone.append(driver_page.find_element_by_xpath(
                    '/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[1]/p/span').text.split('\n')[2])
            #logger.info(phone)
            types = driver_page.find_elements_by_xpath('/html/body/section/section/div[1]/div[3]/div[2]/div[1]/p/span')
            types_t = ''
            for t in types:
                types_t = types_t + ' ' + t.text
            type.append(types_t)
            #logger.info(type)
            hours_of_operation.append(driver_page.find_element_by_xpath(
                '/html/body/section/section/div[1]/div[3]/div[1]/div[3]/div[1]/p').text.replace('\n', ' '))
            #logger.info(hours_of_operation)
            lats_lngs = driver_page.find_element_by_xpath(
                "/html/body/section/section/div[1]/div[3]/div[1]/div[2]/div[2]/div/a[1]").get_attribute('href')
            driver_lat_lng = get_driver()
            driver_lat_lng.get(lats_lngs)
            time.sleep(4)
            latitude.append(
                str(driver_lat_lng.find_element_by_xpath("/html/head/meta[8]").get_attribute("content")).split('=')[
                    1].split('%2C')[0])
            #logger.info(latitude)
            longitude.append(
                str(driver_lat_lng.find_element_by_xpath("/html/head/meta[8]").get_attribute("content")).split('%2C')[
                    1].split('&zoom')[0])
            #logger.info(longitude)

    data = []
    for i in range(0, len(street_address)):
        row = []
        row.append('https://centurynationalbank.com')
        row.append(location_name[i] if location_name[i] else "<MISSING>")
        row.append(street_address[i] if street_address[i] else "<MISSING>")
        row.append(city[i] if city[i] else "<MISSING>")
        row.append(state[i] if state[i] else "<MISSING>")
        row.append(zipcode[i] if zipcode[i] else "<MISSING>")
        row.append("US")
        row.append(ids[i] if ids[i] else "<MISSING>")
        row.append(phone[i] if phone[i] else "<MISSING>")
        row.append(type[i] if type[i] else "<MISSING>")
        row.append(latitude[i] if latitude[i] else "<MISSING>")
        row.append(longitude[i] if longitude[i] else "<MISSING>")
        row.append(hours_of_operation[i] if hours_of_operation[i] else "<MISSING>")
        row.append(pages_url[i] if pages_url[i] else "<MISSING>")

        data.append(row)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
