import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('maxsmexicancuisine_com')




options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

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
        count=0
        data=[]
        driver.get("https://www.maxsmexicancuisine.com/contact")
        page_url = "https://www.maxsmexicancuisine.com/contact"
        time.sleep(10)
        stores = driver.find_elements_by_css_selector('div.txtNew')
        for store in stores:
            try:
                location_name = store.find_element_by_css_selector('h5').text
                street_addr = store.find_element_by_css_selector('p:nth-child(7)').text
                state_city_zip = store.find_element_by_css_selector('p:nth-child(8)').text
                zipcode = state_city_zip.split(" ")[-1]
                state = state_city_zip.split(" ")[-2]
                city = state_city_zip.split(" ")[-3].replace(",", "")
                hours_of_op = store.find_element_by_css_selector('p:nth-child(2)').text + " " + store.find_element_by_css_selector('p:nth-child(3)').text + \
                              " " + store.find_element_by_css_selector('p:nth-child(4)').text
                phone = store.find_element_by_css_selector('p:nth-child(9)').text
                geomap = store.find_element_by_css_selector('p:nth-child(7) > span > a').get_attribute('href')
                lat,lon = parse_geo(geomap)
                data.append([
                        'https://www.maxsmexicancuisine.com/',
                        page_url,
                        location_name,
                        street_addr,
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
                count = count + 1
                logger.info(count)
            except:
                pass

        time.sleep(3)
        driver.quit()
        return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()