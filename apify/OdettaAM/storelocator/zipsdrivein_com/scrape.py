import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('zipsdrivein_com')



options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data = []
    driver.get("http://zipsdrivein.com/locations.html")
    time.sleep(10)
    stores1 = driver.find_elements_by_css_selector('table > tbody > tr > td > div > table:nth-child(3) > tbody > tr > td:nth-child(1) > p')
    stores2 = driver.find_elements_by_css_selector('table > tbody > tr > td > div > table:nth-child(3) > tbody > tr > td:nth-child(2) > p')
    stores3 = driver.find_elements_by_css_selector('table > tbody > tr > td > div > table:nth-child(3) > tbody > tr > td:nth-child(3) > p')
    stores = stores1 + stores2 + stores3
    logger.info(len(stores))
    for store in stores:
        info = store.text
        #if "Airway" in info:
         #logger.info(info)
        li = info.splitlines()
        if len(li) ==4:
            location_name = li[0]
            try:
                loc_link = store.find_element_by_css_selector('font > em > a').get_attribute('href')
                if 'locations/' in loc_link:
                    driver2.get(loc_link)
                    time.sleep(5)
                    hours_of_op = driver2.find_element_by_css_selector('body > table > tbody > tr > td > div > table > tbody > tr:nth-child(6) > td:nth-child(4)').text
                else:
                    hours_of_op = '<MISSING>'
            except:
                try:
                    loc_link = store.find_element_by_css_selector('font > a').get_attribute('href')
                    if 'locations/' in loc_link:
                        driver2.get(loc_link)
                        time.sleep(5)
                        hours_of_op = driver2.find_element_by_css_selector('body > table > tbody > tr > td > div > table > tbody > tr:nth-child(6) > td:nth-child(4)').text
                    else:
                        hours_of_op = '<MISSING>'
                except:
                    hours_of_op = '<MISSING>'
            if location_name == '**NEW LOCATION**':
                location_name = li[1]
                street_addr = li[2]
                state = li[3].split(',')[1].strip()
                city = li[3].split(',')[0]
                phone = '<MISSING>'
            else:
                street_addr = li[1]
                state = li[2].split(',')[1].strip()
                city = li[2].split(',')[0]
                phone = li[3]
        elif len(li) ==3:
            if "Airway" not in info:
           
             location_name = '<MISSING>'
             street_addr = li[0]
             state = li[1].split(',')[1].strip()
             city = li[1].split(',')[0]
             phone = li[2]
             hours_of_op = '<MISSING>'
            else:
             location_name = li[0]
             street_addr = li[1].split(',')[0].replace(li[0].strip(),"").strip()
             state = li[1].split(',')[1].strip()
             city = li[0]
             phone = li[2]
             hours_of_op = '<MISSING>'
        elif len(li) ==5:
            
            location_name = li[0]
            street_addr = li[1]
            state = li[2].split(',')[1].strip()
            city = li[2].split(',')[0]
            phone = li[3]
            hours_of_op = '<MISSING>'
        data.append([
                     'http://zipsdrivein.com/',
                      location_name,
                      street_addr,
                      city,
                      state,
                      '<MISSING>',
                      'US',
                      '<MISSING>',
                      phone,
                      '<MISSING>',
                      '<MISSING>',
                      '<MISSING>',
                       hours_of_op.replace("\n"," ")
                 ])

    time.sleep(3)
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
