import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
    driver.get("https://www.dashsmarket.com/locations/")
    stores = driver.execute_script("return S.mapManager.locations")
    for store in stores:
        location_name = store['name']
        street_address = store['address1']
        state = store['state']
        city = store['city']
        zipcode = store['zipCode']
        phone = store['phone']
        store_number= store['storeID']
        hours_of_op = store['hourInfo']
        lat = store['latitude']
        lon = store['longitude']
        data.append([
             'https://www.dashsmarket.com/',
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              store_number,
              phone,
              '<MISSING>',
              lat,
              lon,
              hours_of_op
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
