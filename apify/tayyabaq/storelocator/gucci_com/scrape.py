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
                
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[];store_no=[];country=[];location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[];location_type=[]
    driver = get_driver()
    countries = ['https://www.gucci.com/us/en/store', 'https://www.gucci.com/ca/en/store']
    for n in range(0,len(countries)):
        driver.get(countries[n])
        time.sleep(3)
        location = driver.find_elements_by_xpath('//h3[@class="name"]/a')
        for n in range(0,len(location)):
            location_name.append(location[n].text)
        lat_lon = driver.find_elements_by_xpath('//ol[@id="stores"]/li')
        for n in range(0,len(lat_lon)):
            latitude.append(lat_lon[n].get_attribute('data-latitude'))
            longitude.append(lat_lon[n].get_attribute('data-longitude'))
            store_no.append(lat_lon[n].get_attribute('data-store-code'))
            location_type.append(lat_lon[n].get_attribute('data-store-type'))
        address = driver.find_elements_by_class_name('address')
        for n in range(0,len(address)):
            street_address.append(address[n].text.split("\n")[0])
            zipcode.append(address[n].text.split("\n")[1].split(",")[-2])
            country.append(address[n].text.split("\n")[1].split(",")[-1])
            city.append(address[n].text.split("\n")[1].split(",")[0])
        for n in range(0,len(address)):
            a=address[n].text.split("\n")[1].split(",")[1].strip()
            if bool(re.match('^[0-9]+$',str(a)))==True:
                state.append('<MISSING>')
            else:
                state.append(a)
        info = driver.find_elements_by_xpath('//div[@class="store-infos"]')
        phones = driver.find_elements_by_xpath('//div[@class="store-infos"]/div[1]')
        for n in range(0,len(info)):
            if "T:" in info[n].text:
                try:
                    phone.append(phones[n].text.split("T:")[1])
                except:
                    phone.append('<MISSING>')
            else:
                phone.append('<MISSING>')
        stores = driver.find_elements_by_xpath('//h3[@class="name"]/a')
        links = [stores[n].get_attribute('href') for n in range(0,len(stores))]
        for n in range(0,len(links)):
            driver.get(links[n])
            hours_of_operation.append(driver.find_element_by_class_name('store-detail-store-hours-table').text)
    for n in range(0,len(street_address)): 
        data.append([
            'https://www.gucci.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            country[n],
            store_no[n],
            phone[n],
            location_type[n],
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
