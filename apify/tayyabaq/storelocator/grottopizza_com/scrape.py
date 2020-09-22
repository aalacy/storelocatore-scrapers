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
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('https://www.grottopizza.com/locations/')
    time.sleep(6)
    if 'class="cta-button italia white-text red-bg align-center centered parent-relative' in str(driver.page_source):
      print('here')
    stores=re.findall(r'<a href="([^"]+)" class="cta-button italia white-text red-bg align-center centered parent-relative',str(driver.page_source))
    store_links = [stores[n].get_attribute('href') for n in range(0,len(stores))]
    print((len(stores)))
    for n in range(1,len(store_links)):
        driver.get(store_links[n])
        time.sleep(2)
        location_name.append(driver.find_element_by_class_name('block-heading').text.replace('\u2013',' '))
        phone.append(driver.find_element_by_xpath("//div[@class='content-holder']/h2").text.replace('\u2013',' ').split("\n")[0])
        address =driver.find_element_by_xpath("//div[@class='content-holder']/p[1]").text.replace('\u2013',' ')
        street_address.append(address.split("\n")[0].split(",")[0])
        city.append(address.split("\n")[1].split(",")[0])
        state.append(address.split("\n")[1].split(",")[1].split()[0].strip())
        zipcode.append(address.split("\n")[1].split(",")[1].split()[1].strip())
        hours_of_operation.append(driver.find_element_by_xpath("//div[@class='content-holder']/p[2]").text.replace('\u2013',' '))
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.grottopizza.com',
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
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
