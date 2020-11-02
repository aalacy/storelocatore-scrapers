import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('intajuice_com')



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
    data=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[];hours_of_operation=[]
    driver = get_driver()
    driver.get('https://www.intajuice.com/locations')
    time.sleep(6)
    store =driver.find_elements_by_xpath("//p[@class='font_8']/span/a")
    stores = [store[n].get_attribute('href') for n in range(0,len(store))]
    for n in range(0,len(stores)):
        driver.get(stores[n])
        time.sleep(6)
        try:
            a=driver.find_elements_by_xpath("//span[contains(@style,'0.01em')]")
            if a==[]:
                a=driver.find_elements_by_xpath("//div[contains(@style,'width: 159px; pointer-events: none;')]")
            try:
                street_address.append(a[0].text.split("\n")[0])
                address = a[0].text.split("\n")[1]
            except:
                street_address.append(a[0].text)
                if "," in a[1].text:
                    address = a[1].text
                else:
                    address = a[2].text
            city.append(address.split(",")[0])
            state.append(address.split(",")[1].split()[0])
            zipcode.append(address.split(",")[1].split()[1])
            phone.append(driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").text)
            location_name.append(driver.find_element_by_css_selector('h3').text)
        except:
            check= driver.find_elements_by_xpath("//div[contains(@style,'font-size:25px; text-align:center;')]")
            logger.info(check)
    for n in range(0,len(location_name)): 
            data.append([
                'https://www.intajuice.com',
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
                '<INACCESSIBLE>'
                ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
