import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
from bs4 import BeautifulSoup
import requests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    driver = get_driver()
    driver.get('https://chaska.coopersfoodsmn.com/location')
    stores=driver.find_elements_by_xpath(("//div[@class='other-sites-select']/select/option"))
    length=len(stores)
    for n in range(0,length):
        store=driver.find_elements_by_xpath(("//div[@class='other-sites-select']/select/option"))
        store[n].click()
        street_address.append(driver.find_element_by_class_name('addressLine1').text)
        a=driver.find_element_by_class_name('cityStateZip').text.split(",")
        city.append(a[0])
        state.append(a[1].split()[0].strip())
        zipcode.append(a[1].split()[1].strip())
        phone.append(driver.find_element_by_class_name('phone').text)
        hours_of_operation.append(driver.find_element_by_class_name('storeHours').text)
    r = requests.get('https://stclair.coopersfoodsmn.com/location')
    soup = BeautifulSoup(r.content, 'html.parser')
    script = soup.findAll('script')
    latlng=re.findall(r'LatLng\((.*?)\);', str(script))
    for n in range(0,len(latlng)):
        latitude.append(latlng[n].split(",")[0])
        longitude.append(latlng[n].split(",")[1])
    for n in range(0,len(street_address)): 
        data.append([
            'https://chaska.coopersfoodsmn.com',
            '<MISSING>',
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
