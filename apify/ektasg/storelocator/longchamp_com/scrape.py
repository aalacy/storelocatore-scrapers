import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json

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
    a=re.findall(r'&daddr=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    #Canada Stores
    driver.get("https://ca.longchamp.com/en/stores")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('a.btn.btn--full.fs-m.lh-1-5.storeloc-store')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    store_ids = [stores[i].get_attribute('data-nid') for i in range(0, len(stores))]

    for i in range(0,len(name)):
            driver2.get(name[i])
            page_url = name[i]
            time.sleep(1)
            location_name = driver2.find_element_by_css_selector('h2.title-gamma.upper.pt-1.pb-05').text
            store_id = store_ids[i]
            addr = driver2.find_element_by_css_selector('#tab-content-list > div > div:nth-child(1) > p').text
            city = addr.split(" ")[-1]
            if city.lower() == "york":
                city = addr.split(" ")[-2] + " " + addr.split(" ")[-1]
            street_addr = addr.replace(city, "")
            state = '<MISSING>'
            zipcode = '<MISSING>'
            try:
                phone = driver2.find_element_by_css_selector('#tab-content-list > div > div:nth-child(3) > p').text.lstrip()
            except:
                phone = driver2.find_element_by_css_selector('#tab-content-list > div > div:nth-child(2) > p').text.lstrip()
            try:
                expandable = WebDriverWait(driver2, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.expandmore__button.js-expandmore-button")))
                expandables = driver2.find_element_by_css_selector('button.expandmore__button.js-expandmore-button')
                expandables.click()
                hours_of_op = driver2.find_element_by_css_selector('div.js-to_expand.animated-expandmore.expandmore__to_expand > div.pb-1').text.replace("\n"," ")
                loc_type = 'BOUTIQUE'
            except:
                hours_of_op = '<MISSING>'
                loc_type = 'REVENDEUR'
            country ="CA"
            try:
                text = driver2.find_element_by_xpath("//script[@type='application/json']").get_attribute('innerHTML')
                req_json = json.loads(text)
                json_data = req_json['geolocation']
                latitude = json_data['lat1']
                longitude = json_data['long1']
            except:
                latitude = '<MISSING>'
                longitude = '<MISSING>'
            data.append([
                        'https://www.longchamp.com/',
                        page_url,
                        location_name,
                        street_addr,
                        city,
                        state,
                        zipcode,
                        country,
                        store_id,
                        phone,
                        loc_type,
                        latitude,
                        longitude,
                        hours_of_op
                    ])
            count = count + 1
            print(count)

    # US Stores
    driver.get("https://us.longchamp.com/stores")
    time.sleep(6)
    stores = driver.find_elements_by_css_selector('a.btn.btn--full.fs-m.lh-1-5.storeloc-store')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    store_ids = [stores[i].get_attribute('data-nid') for i in range(0, len(stores))]

    for i in range(0, len(name)):
        driver2.get(name[i])
        page_url = name[i]
        time.sleep(1)
        try:
            location_name = driver2.find_element_by_css_selector('h2.title-gamma.upper.pt-1.pb-05').text
        except:
            location_name = '<MISSING>'
        try:
            store_id = store_ids[i]
            addr = driver2.find_element_by_css_selector('#tab-content-list > div > div:nth-child(1) > p').text
            city = addr.split(" ")[-1]
            if city.lower() == "york":
                city = addr.split(" ")[-2] + " " + addr.split(" ")[-1]
            street_addr = addr.replace(city, "")
        except:
            store_id = '<MISSING>'
            city = '<MISSING>'
            street_addr = '<MISSING>'
        state = '<MISSING>'
        zipcode = '<MISSING>'
        try:
            phone = driver2.find_element_by_css_selector('#tab-content-list > div > div:nth-child(3) > p').text.lstrip()
            phone = phone.replace(')','').replace('(','').replace('+1','').replace('+','').replace('-','')
        except:
            try:
                phone = driver2.find_element_by_css_selector('#tab-content-list > div > div:nth-child(2) > p').text.lstrip()
                phone = phone.replace(')', '').replace('(', '').replace('+1', '').replace('+', '').replace('-', '')
            except:
                phone = '<MISSING>'
        try:
            expandable = WebDriverWait(driver2, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.expandmore__button.js-expandmore-button")))
            expandables = driver2.find_element_by_css_selector('button.expandmore__button.js-expandmore-button')
            expandables.click()
            hours_of_op = driver2.find_element_by_css_selector('div.js-to_expand.animated-expandmore.expandmore__to_expand > div.pb-1').text.replace("\n", " ")
            loc_type = 'Store'
        except:
            hours_of_op = '<MISSING>'
            loc_type = 'Reseller'
        country = "US"
        try:
            text = driver2.find_element_by_xpath("//script[@type='application/json']").get_attribute('innerHTML')
            req_json = json.loads(text)
            json_data = req_json['geolocation']
            latitude = json_data['lat1']
            longitude = json_data['long1']
        except:
            latitude = '<MISSING>'
            longitude = '<MISSING>'
        data.append([
            'https://www.longchamp.com/',
            page_url,
            location_name,
            street_addr,
            city,
            state,
            zipcode,
            country,
            store_id,
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
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
