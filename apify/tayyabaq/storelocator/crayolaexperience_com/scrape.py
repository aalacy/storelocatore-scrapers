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
def parse_geo(url):
    a=re.findall(r'\&ll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    #Variables
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('https://www.crayolaexperience.com/sitemap')
    time.sleep(6)
    # Fetch stores 
    stores = driver.find_elements_by_link_text("Contact Us")
    loc = [stores[i].get_attribute("href") for i in range(0,len(stores))]
    for i in range(0,len(loc)/2):
        driver.get(loc[i])
        time.sleep(3)
        location_name.append(driver.find_element_by_class_name("section-heading").text)
        address = driver.find_element_by_xpath("//div[@class='text']/p")
        phone.append(driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").text)
        street_address.append(re.findall(r'[\d].*',address.text)[0])
        city.append(address.text.split("\n")[-1].split(",")[0])
        state.append(address.text.split("\n")[-1].split(",")[1].strip().split()[0])
        zipcode.append(address.text.split("\n")[-1].split(",")[1].strip().split()[1])
        try:
            geomap = driver.find_element_by_link_text("Google Directions").get_attribute('href')
            lat, lon = parse_geo(geomap)
            latitude.append(lat)
            longitude.append(lon)
        except:
            latitude.append('<MISSING>')
            longitude.append('<MISSING>')

    for n in range(0,len(location_name)): 
        data.append([
            'https://www.crayolaexperience.com',
            location_name[n],
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
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
