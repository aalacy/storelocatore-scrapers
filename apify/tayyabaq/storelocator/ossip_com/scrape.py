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

def fetch_data():
    data=[]; location_name=[];links=[];countries=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('https://viewer.blipstar.com/map?uid=2396402&gui=true&type=all&rc=&width=auto&style=street&tag=false')
    time.sleep(3)
    location=driver.find_elements_by_class_name('storename')
    stores=driver.find_elements_by_link_text('Location + Doctor Information')
    stores_href=[stores[n].get_attribute('href') for n in range(0,len(stores))]
    address = driver.find_elements_by_class_name('storeaddress')
    cities = driver.find_elements_by_class_name('storecity')
    states = driver.find_elements_by_class_name('storestate')
    zips = driver.find_elements_by_class_name('storepostalcode')
    location_name = [location[n].text for n in range(0,len(location))]
    street_address = [address[n].text.split("\n")[0] for n in range(0,len(address))]
    city = [cities[n].text for n in range(0,len(cities))]
    state = [states[n].text for n in range(0,len(states))]
    zipcode =[zips[n].text for n in range(0,len(zips))]
    for n in range(0,len(stores_href)):
        driver.get(stores_href[n])
        time.sleep(4)
        a=driver.find_elements_by_class_name('paragraph')
        hours_of_operation.append(a[1].text)
        phone.append(a[0].text.split("\n")[3].split("Phone: ")[1])
        lat_lon = driver.find_element_by_tag_name('iframe').get_attribute('src')
        longitude.append(lat_lon.split("long=")[1].split("&")[0])
        latitude.append(lat_lon.split("lat=")[1].split("&")[0])
    for n in range(0,len(street_address)):
        data.append([
            'https://www.ossip.com',
            'https://viewer.blipstar.com/map?uid=2396402&gui=true&type=all&rc=&width=auto&style=street&tag=false',
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
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
