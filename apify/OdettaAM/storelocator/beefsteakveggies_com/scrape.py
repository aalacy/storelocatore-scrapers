import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://beefsteakveggies.com/where-we-are/")
    globalvar = driver.execute_script("return locations;")
    i = 0
    stores = driver.find_elements_by_css_selector('div.contact-box')
    for store in stores:
        location_name = store.find_element_by_css_selector('h2.contact-title').text
        raw_address = store.find_element_by_css_selector('address > p > a').text
        phone = store.find_element_by_css_selector('div.contact-info > p:nth-child(3)').text
        phone = re.sub(r'\D', "", phone)
        if phone == "":
            phone = '<MISSING>'
        latitude = globalvar[i]['lat_lng'].split(',')[0]
        longitude = globalvar[i]['lat_lng'].split(',')[1]
        store_id = globalvar[i]['marker_id']
        hours_of_op = store.find_element_by_css_selector('div.contact-timing').get_attribute('innerHTML')
        hours_of_op = re.sub(r'<p>|</p>|<h3>HOURS</h3>|<br>|&nbsp|\n', "", hours_of_op)
        data.append([
             'http://beefsteakveggies.com/',
              location_name,
              raw_address,
              '<INACCESSIBLE>',
              '<INACCESSIBLE>',
              '<INACCESSIBLE>',
              '<INACCESSIBLE>',
              'US',
              store_id,
              phone,
              '<MISSING>',
              latitude,
              longitude,
              hours_of_op
            ])
        i+=1

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()