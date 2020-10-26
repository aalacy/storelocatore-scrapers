import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('berkshirebank_com')



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

def parse_geo(url):
    lon = re.findall(r'\+(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\center=(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    #Variables
    data=[]; city=[]; zipcode=[]; state=[]; maps=[]; location_type=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('https://www.berkshirebank.com/About/Let-Us-Help/Locations')
    #Close popup
    driver.find_element_by_class_name("close").click()
    time.sleep(15)
    # Fetch stores location name and type
    location = driver.find_elements_by_xpath("//ul[@id='locations']/li/div[1]")
    location_name=[location[n].text for n in range(0,len(location))]
    location_type = [location_name[n].split('at')[0] for n in range(0,len(location_name))]
    # Fetch stores address
    street =driver.find_elements_by_xpath("//ul[@id='locations']/li/div[2]")
    street_address=[street[n].text for n in range(0,len(street))]
    address = driver.find_elements_by_xpath("//ul[@id='locations']/li/div[3]")
    address_store=[address[n].text for n in range(0,len(address))]
    for n in range(0,len(address_store)):
        city.append(address_store[n].split(",")[0])
        state.append(address_store[n].split(",")[1].split()[0])
        zipcode.append(address_store[n].split(",")[1].split()[1])
    time.sleep(3)
    # Fetch More info hyperlinks
    googlemaps = driver.find_elements_by_xpath("//ul[@id='locations']/li/div[4]/a")
    googlemap = [googlemaps[i].get_attribute('href') for i in range(0,len(googlemaps))]
    time.sleep(2)
    # Go to each hyperlink and fetch metadata like lon, lat, phone, hours_of_operation
    for gmap in range(0,len(googlemap)):
        driver.get(googlemap[gmap])
        time.sleep(3)
        lat, lon = parse_geo(driver.find_element_by_css_selector('iframe').get_attribute('src'))
        latitude.append(lat)
        longitude.append(lon)
        logger.info(lat)
        hours = driver.find_element_by_class_name("mb-4").text
        if hours !="":
            hours_of_operation.append(hours)
        else:
            hours_of_operation.append("<MISSING>")   
        try:
            phone.append(driver.find_element_by_xpath("//div[@class='row']/div/p[2]").text.split(":")[1].strip())
        except:
            phone.append("<MISSING>")
    for n in range(0,len(location)): 
        data.append([
            'https://www.berkshirebank.com/',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            location_type[n],
            latitude[n],
            longitude[n],
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
    #Removing empty lines in csv
    rows = csv.reader(open("data.csv", "rb"))
    newrows = []
    for row in rows:
        if row not in newrows:
            newrows.append(row)
    writer = csv.writer(open("data.csv", "wb"))
    writer.writerows(newrows)

scrape()
