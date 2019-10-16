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
    driver.get('https://www.speedycash.com/find-a-store/')
    time.sleep(3)
    stores=driver.find_elements_by_xpath('//svg/a')
    stores_href=[stores[n].get_attribute('href') for n in range(0,len(stores))]
    title = driver.find_elements_by_class_name('no-underline')
    for n in range(0,len(stores_href)):
        driver.get(stores_href[n])
        address = driver.find_elements_by_tag_name('address')
        phones = driver.find_elements_by_xpath("//a[contains(@class,'store-phone')]")
        for n in range(0,len(address)):
            a=address[n].text.split("\n")
            street_address.append(' '.join(a[:-2]))
            lat,lon = parse_geo(address[n].get_attribute('href'))
            latitude.append(lat)
            longitude.append(lon)
            city.append(a[-1].split(",")[0])
            state.append(a[-1].split(",")[1].split()[0])
            zipcode.append(a[-1].split(",")[1].split()[1])
            phone.append(phones[n].text)
            location_name.append(title[n].text)
    for n in range(0,len(street_address)):
        data.append([
            'https://www.speedycash.com',
            'https://www.speedycash.com/find-a-store/',
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
