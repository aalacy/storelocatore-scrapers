import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\&ll=(--?[\d\.]*)', url)[0]
    return lat,lon
                     
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    driver = get_driver()
    driver.get('https://hotdogonastick.olo.com/locations')
    location = driver.find_elements_by_xpath('//a[contains(@href,"/locations/")]')
    location_href=[location[n].get_attribute('href') for n in range(0,len(location))]
    for n in range(0,len(location_href)):
        driver.get(location_href[n])
        time.sleep(3)
        loc = driver.find_elements_by_xpath('//li[@class="vcard"]/h2/a/span')
        address =driver.find_elements_by_xpath('//div[contains(@class,"streetaddress")]')
        cities = driver.find_elements_by_class_name('locality')
        states = driver.find_elements_by_class_name('region')
        phones = driver.find_elements_by_class_name('location-tel-number')
        hours = driver.find_elements_by_class_name('location-hours')
        lat = driver.find_elements_by_xpath('//span[@class="latitude"]/span')
        lon = driver.find_elements_by_xpath('//span[@class="longitude"]/span')
        for n in range(0,len(loc)):
            location_name.append(loc[n].text)
            street_address.append(address[n].text.split("\n")[0])
            city.append(cities[n].text)
            state.append(states[n].text)
            phone.append(phones[n].text)
            latitude.append(lat[n].get_attribute('title'))
            longitude.append(lon[n].get_attribute('title'))
            hours_of_operation.append(hours[n].text)
    for n in range(0,len(street_address)): 
        data.append([
            'https://hotdogonastick.olo.com/',
            'https://hotdogonastick.olo.com/locations',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            '<MISSING>',
            'US',
            '<MISSING>',
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
