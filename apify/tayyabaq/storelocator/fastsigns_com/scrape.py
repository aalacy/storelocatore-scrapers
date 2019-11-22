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
    driver.get('https://www.fastsigns.com/worldwide')
    time.sleep(3)
    driver.find_element_by_xpath("//select[@name='DataTables_Table_0_length']/option[5]").click()
    stores = driver.find_elements_by_xpath('//tbody/tr/td/a')
    stores_href=[stores[n].get_attribute('href') for n in range(0,len(stores))]
    stores_text = [stores[n].text for n in range(0,len(stores))]
    country = driver.find_elements_by_xpath('//tbody/tr/td[5]')
    address_type = driver.find_elements_by_xpath('//tbody/tr/td[2]')
    for n in range(0,len(stores_href)):
        if ('COMING SOON' not in address_type[n].text) and (('US' in country[n].text) or ('CA' in country[n].text)):
            links.append(stores_href[n])
            location_name.append(stores_text[n])
            countries.append(country[n].text)
    for n in range(0,len(links)):
        driver.get(links[n])
        time.sleep(5)
        address = driver.find_element_by_class_name('address').text
        street_address.append(address.split("\n")[0].split(",")[0])
        city.append(address.split("\n")[0].split(",")[1])
        state.append(address.split("\n")[0].split(",")[2])
        zipcode.append(address.split("\n")[0].split(",")[-1])
        phone.append(driver.find_element_by_class_name('phone').text)
        hours_of_operation.append(driver.find_element_by_xpath('//div[@class="inner"]/div[3]').text)
        lat_lon = b=driver.find_element_by_xpath('//a[contains(@href,"https://www.google.com/maps")]').get_attribute('href')
        try:
            latitude.append(lat_lon.split("n/")[1].split(",")[0])
        except:
            latitude.append('<MISSING>')
        try:
            longitude.append(lat_lon.split("n/")[1].split(",")[1])
        except:
            longitude.append('<MISSING>')
    for n in range(0,len(street_address)):
        data.append([
            'http://fastsigns.com',
            'https://www.fastsigns.com/worldwide',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            countries[n],
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
