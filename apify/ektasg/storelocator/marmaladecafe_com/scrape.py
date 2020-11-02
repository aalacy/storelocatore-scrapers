import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('marmaladecafe_com')




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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://marmaladecafe.com/locations")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.uk-panel.uk-panel-box')
    for store in stores:
        location_name= store.find_element_by_css_selector('a.uk-link-reset').text
        info = store.find_element_by_css_selector('div.uk-margin > p:nth-child(1)').text.splitlines()
        phone = info[-2]
        state_city_zip =  info[-3]
        zipcode = state_city_zip.split(" ")[-1]
        state = state_city_zip.split(" ")[-2]
        city = state_city_zip.split(",")[0]
        street_addr = info[-4]
        hours_of_op = store.find_element_by_css_selector('div.uk-margin > p:nth-child(2) ').text
        data.append([
                'https://marmaladecafe.com/',
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone,
                '<MISSING>',
                '<MISSING>',
                '<MISSING>',
                hours_of_op
            ])
        count = count + 1
        logger.info(count)

    geomaps = store.find_elements_by_xpath("//a[contains(@href,'https://goo.gl/maps')]")
    geo_url = [geomaps[i].get_attribute('href') for i in range(0,len(geomaps))]
    for i in range(0,len(geo_url)):
        driver2.get(geo_url[i])
        time.sleep(10)
        lat, lon = parse_geo(driver2.current_url)
        data[i][10] = lat
        data[i][11] = lon

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()