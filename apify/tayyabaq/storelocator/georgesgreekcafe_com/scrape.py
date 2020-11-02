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
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    #Variables
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('https://www.georgesgreekcafe.com/locations/')
    time.sleep(6)
    # Fetch stores
    names = driver.find_elements_by_class_name("card__btn")
    name = [names[i].get_attribute('href') for i in range(0,len(names))]
    location_name = [names[i].text for i in range(0,len(names))]
    for i in range(0,len(name)):
        driver.get(name[i])
        time.sleep(3)
        address = driver.find_element_by_xpath("//div[@class='col-md-6']/p[1]").text
        stores = driver.find_elements_by_xpath("//a[contains(@href, 'https://www.google.com/maps')]")
        lat,lon = parse_geo(stores[0].get_attribute('href'))
        latitude.append(lat)
        longitude.append(lon)
        street_address.append(address.split("\n")[0])
        phone.append(address.split("\n")[-1])
        city.append(address.split("\n")[1].split(",")[0])
        zipcode.append(address.split("\n")[1].split(",")[1].strip().split()[1])
        state.append(address.split("\n")[1].split(",")[1].strip().split()[0])
        hours_of_operation.append(driver.find_element_by_xpath("//div[@class='col-md-6']/p[2]").text)
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.georgesgreekcafe.com',
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
