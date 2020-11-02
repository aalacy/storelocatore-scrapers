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
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    #Variables
    data=[]; store_no=[];zipcode=[];hours_of_operation=[];location_name=[];location_type=[];city=[];street_address=[]; state=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('https://www.sturdevants.com/store-locator/')
    time.sleep(10)
    driver.find_element_by_xpath("//select[@name='wpgmza_table_2_length']/option[text()='100']").click()
    # Fetch stores
    time.sleep(6)
    stores = driver.find_elements_by_xpath("//table[@id='wpgmza_table_2']/tbody/tr/td")
    time.sleep(2)
    for i in range(1,len(stores),6):
        location_name.append(stores[i].text)
    for i in range(3,len(stores),6):
        a=stores[i].text.split(",")
        if len(a)>4:
            street_address.append(a[0]+a[1])
            city.append(a[2].strip())
        else:
            street_address.append(a[0])
            city.append(a[1].strip())
        try:
            state.append(stores[i].text.split(",")[-2].strip())
            zipcode.append(stores[i].text.split(",")[-2].strip().split()[1])
        except:
            state.append(stores[i].text.split(",")[-2].strip())
            zipcode.append("<MISSING>")
    for i in range(4,len(stores),6):
        phone.append(stores[i].text.split("\n")[0].split("Phone: ")[1])
        hours_of_operation.append(stores[i].text.split("\n")[1])
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.sturdevants.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<INACCESSIBLE>',
            '<INACCESSIBLE>',
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape() 
