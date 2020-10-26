import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('papavinositaliankitchen_com')



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
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data=[]
    count=0
    driver.get("http://www.papavinositaliankitchen.com/locations-hours-contact/")
    time.sleep(5)
    stores = driver.find_elements_by_css_selector('div.desc_wrapper')
    page_url = "http://www.papavinositaliankitchen.com/locations-hours-contact/"
    hours_of_op = driver.find_element_by_css_selector('div.opening_hours_wrapper').text.replace("\n", " ")
    for store in stores:
            location_name = store.find_element_by_css_selector('h4').get_attribute('textContent')
            flag = store.find_element_by_css_selector('h4 >img').get_attribute('src')
            if 'spmapflag' in flag:
                loc_type = 'Spageddies'
            else:
                loc_type = 'PapaVinos'
            logger.info("location_name........" , location_name)
            address = store.find_element_by_css_selector('div.desc > strong').get_attribute('textContent').splitlines()
            street_addr = address[0]
            state_city_zip = address[1]
            city= state_city_zip.split(",")[0]
            zipcode = state_city_zip.split(",")[1].split(" ")[-1]
            state = state_city_zip.split(",")[1].split(" ")[-2]
            phone =store.find_element_by_css_selector('p.phone').get_attribute('textContent')
            data.append([
                 'http://www.papavinositaliankitchen.com',
                  page_url,
                  location_name,
                  street_addr,
                  city,
                  state,
                  zipcode,
                  'US',
                  '<MISSING>',
                  phone,
                  loc_type,
                  '<MISSING>',
                  '<MISSING>',
                  hours_of_op
                ])
            count+=1
            logger.info(count)

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()