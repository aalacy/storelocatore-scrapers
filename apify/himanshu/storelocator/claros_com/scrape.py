import csv
import os
from sgrequests import SgRequests
from bs4 import BeautifulSoup
session = SgRequests()
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import platform
system = platform.system()

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if "linux" in system.lower():
        return webdriver.Firefox(executable_path='./geckodriver', options=options)        
    else:
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    # print("~~~~addy~~",addy)
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    # print(state_zip)
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.claros.com/'

    driver = get_driver()
    driver.get(locator_domain)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'contact-')]")
    link_list = []
    for href in hrefs:
        if 'us' not in href.get_attribute('href'):
            link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        page_url = link
        # driver.implicitly_wait(10)
        r=session.get(link)
        lat=''
        log=''
        location_soup = BeautifulSoup(r.text,"lxml")
        lat = str(location_soup).split("{ zoom:")[1].split("}, key,")[0].replace(" 14, lat: ",'').replace("lng:",'').split(',')[0].strip()
        log = str(location_soup).split("{ zoom:")[1].split("}, key,")[0].replace(" 14, lat: ",'').replace("lng:",'').split(',')[1].strip()
        # print(log)
        # print(list(location_soup.find_all("div",{"class":"txt"})[1].stripped_strings))
        full = list(location_soup.find_all("div",{"class":"txt"})[1].stripped_strings)
        if len(full)==1:
            full1 = list(location_soup.find_all("div",{"class":"txt"})[0].stripped_strings)
            street_address = full1[0]
            city, state, zip_code = addy_ext(full1[1])
            # print(street_address,"~~~~~~~~~~~~~~~~~~~~~",link)
        else:

            street_address = full[0]
            city, state, zip_code = addy_ext(full[1])
     

        phones = list(location_soup.find_all("div",{"class":"txt"})[3].stripped_strings)
        hours = " ".join(list(location_soup.find_all("div",{"class":"txt"})[4].stripped_strings))

        
      

        phone_number = phones[-1].replace("Serving you for over 13 years",'626-446-0275')
        # print(phone_number)

    

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        location_name = city
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, log, hours.replace('Open ',''),page_url]
        all_store_data.append(store_data)
        # print(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
