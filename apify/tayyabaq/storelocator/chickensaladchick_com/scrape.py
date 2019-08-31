import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
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
    driver.get('https://www.chickensaladchick.com/locations/')
    phones=driver.find_elements_by_xpath('//div[contains(@class,"phone")]/a')
    phone=[str(phones[n].get_attribute('href')).split("tel:")[1] for n in range(0,len(phones))]
    name = driver.find_elements_by_xpath("//li[@class='location']")
    location_name = [name[n].get_attribute('data-name') for n in range(0,len(name))]
    longitude = [name[n].get_attribute('data-longitude') for n in range(0,len(name))]
    latitude = [name[n].get_attribute('data-latitude') for n in range(0,len(name))]
    city = [name[n].get_attribute('data-city') for n in range(0,len(name))]
    state = [str(name[n].get_attribute('data-state')).upper() for n in range(0,len(name))]
    zipcode = [name[n].get_attribute('data-zip') for n in range(0,len(name))]
    address = driver.find_elements_by_tag_name('address')
    street_address = [address[n].text.split("\n")[0] for n in range(0,len(address))]
    hours = driver.find_elements_by_xpath('//div[@class="hours-container"]')
    hours_of_operation = [hours[n].text for n in range(0,len(hours))]
    for n in range(0,len(street_address)): 
        data.append([
            'https://www.chickensaladchick.com',
            '<MISSING>',
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
