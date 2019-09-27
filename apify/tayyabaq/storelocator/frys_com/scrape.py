import csv
import os
import requests
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
    driver.get('https://www.frys.com/ac/storeinfo/storelocator/?site=csfooter_B')
    location = driver.find_elements_by_xpath('//td[@id="tablefont3"]/a[contains(@href,"/ac/storeinfo/")]')
    location_href=[location[n].get_attribute('href') for n in range(0,len(location))]
    location_name = [location[n].text for n in range(0,len(location))]
    for n in range(0,len(location_href)):
        driver.get(location_href[n])
        time.sleep(3)
        address = driver.find_element_by_id('address').text
        street_address.append(address.split("\n")[0])
        city.append(address.split("\n")[1].split(",")[0])
        state.append(address.split("\n")[1].split(",")[1].split()[0])
        zipcode.append(address.split("\n")[1].split(",")[1].split()[1])
        phone.append(address.split("\n")[2].split("Phone ")[1])
        try:
            lat_lon= driver.find_element_by_xpath('//a[contains(@href,"www.google.com/")]')
            lat,lon=parse_geo(str(lat_lon.get_attribute('href')))
            if (lat=="") or (lat==[]):
                latitude.append('<MISSING>')
            else:
                latitude.append(lat)
            if (lon=="") or (lon==[]):
                longitude.append('<MISSING>')
            else:
                longitude.append(lon)
        except:
            latitude.append('<MISSING>')
            longitude.append('<MISSING>')
    for n in range(0,len(street_address)): 
        data.append([
            'https://www.frys.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            '<INACCESSIBLE>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
