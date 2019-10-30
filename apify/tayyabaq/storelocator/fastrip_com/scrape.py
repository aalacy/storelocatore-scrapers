import csv
import os, time
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
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[];store_number=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    driver = get_driver()
    driver.get('http://fastrip.com/index.php/store-locations')
    time.sleep(3)
    driver.find_element_by_xpath('//select[@id="radiusSelect"]/option[5]').click()
    stores = driver.find_elements_by_class_name('loc-address')
    tags = driver.find_elements_by_class_name('loc-tags')
    location_type = [tags[n].text for n in range(0,len(tags))]
    for n in range(0,len(stores)-1):
        try:
            state.append(stores[n].text.split(",")[2].split()[0].split(".")[0].upper())
            city.append(stores[n].text.split(",")[1])
            street_address.append(stores[n].text.split(",")[0])
            zipcode.append(stores[n].text.split(",")[2].split()[1])
        except:
            a=' '.join(stores[n].text.split(".")[1:])
            state.append(a.split()[-2].strip().split(".")[0].upper())
            city.append(a.split()[-3].split(",")[0].strip())
            street_address.append(stores[n].text.split(".")[0])
            zipcode.append(a.split()[-1].strip())
    loc = driver.find_elements_by_class_name('loc-name')
    location_name = [loc[n].text for n in range(0,len(loc))]
    store_number= [loc[n].text.split("#")[1].strip() for n in range(0,len(loc))]
    phones = driver.find_elements_by_class_name('loc-phone')
    phone = [phones[n].text for n in range(0,len(phones))]
    for n in range(0,len(street_address)): 
        data.append([
            'http://fastrip.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            store_number[n],
            phone[n],
            location_type[n],
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
