import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument("--disable-notifications")    
options.add_argument('disable-infobars')
options.add_argument('--disable-dev-shm-usage')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    data = []
    p = 0
    #driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
    
   
    i = 0 
    while True:
        #driver = webdriver.Chrome("c:\\Users\\Dell\\local\\chromedriver", options=options)
        driver = webdriver.Chrome("chromedriver", options=options)
        driver.get("https://www.shopgalafresh.com/")
        time.sleep(2)
       
       
       
        driver.find_element_by_xpath("//button[contains(text(),'select')]").click()
        time.sleep(2)
        clickElements = driver.find_elements_by_xpath("//button[text()='Choose']")
        clickElements[i].click()
        length = len(clickElements)
       
        time.sleep(3)
        driver.get("https://www.shopgalafresh.com/retailer/information")
        #time.sleep(2)
        #driver.find_element_by_xpath("//button[text()='OK']").click()
        print('clicked;')
        time.sleep(3)
            
        
        
        locname = driver.find_element_by_xpath("//div[@class='branch-name']").text
        streetaddress1 = driver.find_element_by_xpath("//div[@class='branch-address']").text
        hour = driver.find_element_by_xpath("//span[@class='branch-hours']").text
        #time.sleep(10)

        phone = driver.find_element_by_xpath("//a[contains(text(),'(')]").text
        city = streetaddress1.split(',')[len(streetaddress1.split(',')) - 1].split(' ')[1]
        zipcode = "<MISSING>"
        country = "USA"
        if (i == 0 or i == 2):
            state = streetaddress1.split(',')[len(streetaddress1.split(',')) - 1].split(' ')[2]
        else:
            city = streetaddress1.split(',')[len(streetaddress1.split(',')) - 2]
            state = streetaddress1.split(',')[len(streetaddress1.split(',')) - 1].split(' ')[1]

        lat = '<MISSING>'
        lng = '<MISSING>'
        streetaddress = streetaddress1.split(',')[0]

        data.append([
            'https://www.shopgalafresh.com/',
            'https://www.shopgalafresh.com/retailer/information',
            locname,
            streetaddress,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            lng,
            hour
        ])

        #print(i,data[i])
        if i == length -1:
            break
        if i < length:
            i += 1
        else:
            break

        driver.quit()
        
    return data 
  

def scrape():
    data = fetch_data()
    write_output(data)
    


data = scrape()
