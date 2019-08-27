import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options()
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.malinandgoetz.com/'
    ext = 'storelocator/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    pop = driver.find_elements_by_xpath('//img[@data-popup-image-type="square_new"]')
    if len(pop) == 1:
        pop = driver.find_element_by_xpath('//img[@data-popup-image-type="square_new"]')
        driver.execute_script("arguments[0].click();", pop)

    driver.execute_script('MapManager.prototype.updateCountLabel = (() => console.log("update count label"))')
    try: driver.execute_script('window.onload()')
    except: print("failed")
    man = driver.execute_script('return mapManager.markers.reduce((accumulator, marker) => ({ ...accumulator, [marker.storelocator_id]: [marker.position.lat(), marker.position.lng()] }),{})')
    print(man)


    all_store_data = []
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
