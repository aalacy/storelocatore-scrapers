import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json


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
    count=0
    data=[]
    driver.get("https://mtmtavern.com/Locations")
    time.sleep(10)
    stores = driver.find_elements_by_link_text('Menu, Directions & More >')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    time.sleep(5)
    for i in range(0,len(name)):
        driver.get(name[i])
        time.sleep(5)
        text = driver.find_element_by_xpath("//script[@type='application/ld+json']").get_attribute('innerHTML')
        req_json = json.loads(text)
        location_name= req_json['name']
        loc_type = req_json['@type']
        street_addr = req_json['address']['streetAddress']
        city = req_json['address']['addressLocality']
        state = req_json['address']['addressRegion']
        zipcode = req_json['address']['postalCode']
        latitude = req_json['geo']['latitude']
        longitude = req_json['geo']['longitude']
        phone = req_json['contactPoint']['telephone']
        hours_of_op = req_json['openingHours']
        data.append([
                'https://mtmtavern.com/',
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone,
                loc_type,
                latitude,
                longitude,
                hours_of_op
            ])
        count = count + 1
        print(count)

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()