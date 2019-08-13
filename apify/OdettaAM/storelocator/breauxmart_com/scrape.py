import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress


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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://www.breauxmart.com/my-store/store-locator")
    time.sleep(10)
    stores = driver.find_elements_by_class_name('fp-panel-item-wrapper')
    for store in stores:
        location_name = store.find_element_by_css_selector('div.fp-store-title >div > a').text
        tagged_addr = usaddress.tag(store.find_element_by_css_selector('div.fp-store-address').text)[0]
        street_address = tagged_addr['AddressNumber']+ " " + tagged_addr['StreetName'] + " " + tagged_addr['StreetNamePostType'].split('\n')[0]
        city = tagged_addr['PlaceName']
        state = tagged_addr['StateName']
        zipcode = tagged_addr['ZipCode']
        phone = store.find_element_by_css_selector('div.fp-store-phone > p').text
        phone = phone.split('Fax')[0]
        hours_of_op = store.find_element_by_css_selector('div.fp-panel-store-hours > p').text
        store_number = store.get_attribute('data-store-number')
        data.append([
             'https://www.breauxmart.com/',
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              store_number,
              phone,
              '<MISSING>',
              '<MISSING>',
              '<MISSING>',
              hours_of_op
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()