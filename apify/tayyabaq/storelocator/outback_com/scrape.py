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
    driver.get('https://www.outback.com/locations/directory')
    time.sleep(3)
    driver.find_element_by_xpath("//span[contains(@class,'glf-icon_close')]").click()
    state_opt = driver.find_elements_by_xpath("//select[contains(@class,'ng-pristine')]/option")
    state_options = [state_opt[n].text for n in range(0,len(state_opt))]
    for n in range(1,len(state_options)):
        time.sleep(3)
        print (state_options[n])
        driver.find_element_by_xpath("//select[contains(@class,'glf-icon_close')]/option[text()='%s']"%state_options[n]).click()
        driver.wait(3)
        location = driver.find_elements_by_class_name('ng-binding')
        for n in range(0,len(location),2):
            location_name.append(location[n].text)
        for n in range(1,len(location),2):
            street_address.append(location[n].text)
        for n in range(2,len(location),2):
            city.append(location[n].text.split(",")[0])
            state.append(location[n].text.split(",")[1].split()[0])
            zipcode.append(location[n].text.split(",")[1].split()[-1])
        phones = driver.find_elements_by_class_name('phone')
        for n in range(0,len(phones)):
            phone.append(phones[n].text)
    for n in range(0,len(street_address)):
        data.append([
            'https://www.outback.com/',
            'https://www.outback.com/locations/directory',
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
