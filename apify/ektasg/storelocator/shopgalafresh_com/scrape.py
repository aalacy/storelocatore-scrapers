import time
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('shopgalafresh_com')



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
        logger.info('clicked;')
        time.sleep(3)
   
        soup =  str(BeautifulSoup(driver.page_source,'html.parser'))
        #start = soup.find(':"House number","isChecked":false}],"branches":[')
        start = 0
        logger.info(start)
        for m in range(0,4):            
            start = soup.find('branches":[{"id"',start)+1
            temp = soup[start :100]
            logger.info(m,start,temp)
        logger.info(start)   
        start = soup.find('"id"',start)
        start = soup.find(':',start)+1
        end = soup.find(',',start)
        store = soup[start:end]
        start = soup.find('"name"',end)
        start = soup.find(':',start)
        start = soup.find('"',start)+1
        end = soup.find('"',start)
        title = soup[start:end]
        start = soup.find('"location"',end)
        start = soup.find(':',start)
        start = soup.find('"',start)+1
        end = soup.find('"',start)
        street = soup[start:end]
        start = soup.find('"phone"',end)
        start = soup.find(':',start)
        start = soup.find('"',start)+1
        end = soup.find('"',start)
        phone = soup[start:end]
        start = soup.find('"openHours"',end)
        start = soup.find(':',start)
        start = soup.find('"',start)+1
        end = soup.find('"',start)
        hours = soup[start:end]
        start = soup.find('"city"',end)
        start = soup.find(':',start)
        start = soup.find('"',start)+1
        end = soup.find('"',start)
        city = soup[start:end]
        city,state = city.split(' ')
        start = soup.find('"zipCode"',end)
        start = soup.find(':',start)
        start = soup.find('"',start)+1
        end = soup.find('"',start)
        pcode = soup[start:end]
        city = city.replace(',','')
        lat = '<MISSING>'
        lng = '<MISSING>'
        
        hours = hours.replace('<br>','')
        data.append([
            'https://www.shopgalafresh.com/',
            'https://www.shopgalafresh.com/retailer/information',
            title,
            street,
            city,
            state,
            pcode,
            'US',
            store,
            phone,
            '<MISSING>',
            lat,
            lng,
            hours
        ])

        #logger.info(i,data[i])
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
