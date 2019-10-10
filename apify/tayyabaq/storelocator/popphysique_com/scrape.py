import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver=get_driver()
    driver.get('https://popphysique.com/locations')
    stores=driver.find_elements_by_class_name('pg-title-link')
    location = [stores[n].get_attribute('href') for n in range(0,len(stores))]
    for n in range(0,len(location)):
        driver.get(location[n])
        time.sleep(3)
        address=driver.find_elements_by_class_name("is-content")
        if re.search(r'\d-',address[7].text)!=None:
            phone.append(address[7].text)
        else:
            phone.append('<MISSING>')
        for n in range(5,len(address)):
            if '\n' in address[n].text:
                location_name.append(address[5].text)
                street_address.append(address[n].text.split("\n")[0])
                city.append(address[n].text.split("\n")[1].split(",")[0])
                state.append(address[n].text.split("\n")[1].split(",")[1].split()[0])
                zipcode.append(address[n].text.split("\n")[1].split(",")[1].split()[1])
                break
    for n in range(0,len(location_name)):
        data.append([
            'https://www.popphysique.com',
            location_name[n],
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
            '<MISSING>'
        ])
    driver.quit()
    return data
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
