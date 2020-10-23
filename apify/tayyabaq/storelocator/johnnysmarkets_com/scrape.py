import csv
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('johnnysmarkets_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url","location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def parse_geo(url):
    try:
        lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        lat = re.findall(r'\=(-?[\d\.]*)', url)[0]
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    return lat, lon
    
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    #return webdriver.Chrome('c:/chromedriver.exe', chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    driver = get_driver()
    driver.get('http://johnnysmarkets.com/#locations')
    time.sleep(8)
    stores = driver.find_elements_by_xpath("//span[@itemprop='name']")
    location_name = [stores[n].text for n in range(0,len(stores))]
    address = driver.find_elements_by_xpath("//span[@itemprop='streetAddress']")
    street_address = [address[n].text for n in range(0,len(address))]
    cities = driver.find_elements_by_xpath("//span[@itemprop='addressLocality']")
    city = [cities[n].text for n in range(0,len(cities))]
    states = driver.find_elements_by_xpath("//span[@itemprop='addressRegion']")
    state = [states[n].text for n in range(0,len(states))]
    zipcodes = driver.find_elements_by_xpath("//span[@itemprop='postalCode']")
    zipcode = [zipcodes[n].text for n in range(0,len(zipcodes))]
    phones = driver.find_elements_by_xpath("//span[@itemprop='telephone']")
    hour = driver.find_elements_by_class_name("location-details")
    showdetails = driver.find_elements_by_class_name("show-details-btn")
    for n in range(0,len(phones)):
        if (phones[n].text!=[]) and (phones[n].text!=""):
            phone.append(phones[n].text)
        else:
            phone.append('<MISSING>')
    for n in range(0,len(showdetails)):
        showdetails[n].click()
    for n in range(0,len(hour)):
        s=hour[n].text.split("Products")[0]
        if ("Open" in s):
            hours_of_operation.append(s.replace("\n"," "))
        else:
            hr=hour[n].find_elements_by_class_name("store-hours")
            s="Hours "
            dt=hr[0].find_elements_by_tag_name('dt')
            dd=hr[0].find_elements_by_tag_name('dd')
            for m in range(0,len(dt)):
                s=s+dt[m].text+" "
                s=s+dd[m].text+" "
            logger.info(s)
            hours_of_operation.append(s)
    geomap = driver.find_elements_by_xpath("//a[contains(@href,'https://maps.google.com/')]")
    for n in range(0,len(geomap)):
        lat,lon = parse_geo(geomap[n].get_attribute('href'))
        latitude.append(lat)
        longitude.append(lon)
    for n in range(0,len(street_address)):
        data.append([
            'http://johnnysmarkets.com',
            'http://johnnysmarkets.com/#locations',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<INACCESSIBLE>',
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
