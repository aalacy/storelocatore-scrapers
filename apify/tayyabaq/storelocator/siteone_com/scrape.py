import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def parse_geo(url):
    lon = re.findall(r'\%2C(--?[\d\.]*)', url)[0]
    lat = re.findall(r'addr=,(-?[\d\.]*)', url)[0]
    return lat,lon

def fetch_data():
    data=[]; location_name=[];links=[];countries=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('https://www.siteone.com/store-directory')
    time.sleep(3)
    states = driver.find_element_by_xpath("//a[contains(@href,'/store-directory')]")
    state_href=[states[n].get_attribute('href') for n in range(0,len(states))]
    for n in range(0,len(state_href)):
        driver.get(state_href[n])
        time.sleep(3)
        stores = driver.find_elements_by_id('store_directory')
        stores_href = [stores[n].get_attribute('href') for n in range(0,len(stores))]
        for n in range(0,len(stores)):
            driver.get(stores_href[n])
            time.sleep(2)
            location_name.append(driver.find_element_by_xpath('//span[contains(@class,"store_details_name")]').text)
            store_number.append(driver.find_element_by_class_name('store-number-class').text)
            phone.append(driver.find_element_by_xpath('//a[contains(@class,"tel-phone")]').text)
            hours_of_operation.append(driver.find_element_by_xpath('//div[contains(@class,"detailSection")]').text)
            address = driver.find_element_by_xpath('//li[@class="row"]/li').text
            street_address.append(address.split("\n")[0])
            city.append(address.split("\n")[1].split(",")[0])
            state.append(address.split("\n")[1].split(",")[1].split()[0])
            zipcode.append(address.split("\n")[1].split(",")[1].split()[-1])
            geomap=driver.find_element_by_id('storedetailMap')
            latitude.append(geomap.get_attribute('data-mylatitude'))
            longitude.append(geomap.get_attribute('data-mylongitude'))
    for n in range(0,len(street_address)):
        data.append([
            'https://www.siteone.com/',
            'https://www.siteone.com/store-directory',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            store_number[n],
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
