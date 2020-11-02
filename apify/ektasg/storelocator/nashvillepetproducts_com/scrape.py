import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nashvillepetproducts_com')



options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://nashvillepetproducts.com/locations/")
    stores = driver.find_elements_by_css_selector('p.wp-caption-text')
    count =0
    for store in stores:
        page_url = "http://nashvillepetproducts.com/locations/"
        info = store.text.splitlines()
        location_name = info[0]
        street_address= info[1]
        phone = info[-2]
        hours_of_op = info[-4] + " " + info[-3]
        if 'AM' in phone:
            phone = info[-4]
            hours_of_op = info[-3] + " " + info[-2]
        state_city_zip = info[2]
        if '(' in state_city_zip:
            state_city_zip = info[3]
        zipcode = state_city_zip.split(" ")[-1]
        state = state_city_zip.split(" ")[-2]
        if ',' in state_city_zip:
            city = state_city_zip.split(",")[0]
        else:
            city = state_city_zip.split(" ")[-3]
        geomap = store.find_element_by_css_selector('a').get_attribute('href')
        driver2.get(geomap)
        time.sleep(5)
        lat,lon = parse_geo(driver2.current_url)
        data.append([
             'http://nashvillepetproducts.com/',
              page_url,
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              '<MISSING>',
              phone,
              '<MISSING>',
              lat,
              lon,
              hours_of_op
            ])
        count+=1
        logger.info(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()