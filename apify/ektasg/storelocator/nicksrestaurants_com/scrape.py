import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('nicksrestaurants_com')



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
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    a=re.findall(r'\&ll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon

def parse_geo2(url):
    a=re.findall(r'\&sll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon

def parse_geo3(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("http://nicksrestaurants.com/locations/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.span12 >  h2 > a')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    time.sleep(5)
    location_names = [stores[i].text for i in range(0,len(stores))]
    for i in range(0,len(name)):
        driver.get(name[i])
        time.sleep(5)
        try:
            page_url = name[i]
            address =  driver.find_element_by_css_selector('div.tp-caption.small_text.tp-fade.tp-resizeme.start > a').text.splitlines()
            street_addr = address[0]
            city = address[1].split(",")[0]
            state = address[1].split(" ")[-2]
            zipcode = address[1].split(" ")[-1]
            geomap = driver.find_element_by_css_selector('div.tp-caption.small_text.tp-fade.tp-resizeme.start > a').get_attribute('href')
            try:
                lat,lon = parse_geo(geomap)
            except:
                try:
                    lat,lon = parse_geo2(geomap)
                except:
                    lat,lon = parse_geo3(geomap)
            info = driver.find_element_by_css_selector('div.tp-caption.small_text.tp-fade.tp-resizeme.start').text
            phone = info.splitlines()[2]
            hours_of_op = info.split('HOURS')[1].split('GENERAL')[0]
            data.append([
                'http://nicksrestaurants.com/',
                page_url,
                location_names[i],
                street_addr,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone,
                '<MISSING>',
                lat,
                lon,
                hours_of_op
            ])
            count+=1
            logger.info(count)
        except:
            try:
                page_url = name[i]
                address = driver.find_element_by_css_selector('div.tp-caption.small_text.lfr.tp-resizeme.start > a').text.splitlines()
                street_addr = address[0]
                city = address[1].split(",")[0]
                state = address[1].split(" ")[-2]
                zipcode = address[1].split(" ")[-1]

                geomap = driver.find_element_by_css_selector(
                    'div.tp-caption.small_text.lfr.tp-resizeme.start > a').get_attribute('href')
                try:
                    lat, lon = parse_geo(geomap)
                except:
                    try:
                        lat, lon = parse_geo2(geomap)
                    except:
                        lat, lon = parse_geo3(geomap)
                info = driver.find_element_by_css_selector('div.tp-caption.small_text.lfr.tp-resizeme.start').text
                phone = info.splitlines()[2]
                hours_of_op = info.split('HOURS')[1].split('GENERAL')[0]
                data.append([
                    'http://nicksrestaurants.com/',
                    page_url,
                    location_names[i],
                    street_addr,
                    city,
                    state,
                    zipcode,
                    'US',
                    '<MISSING>',
                    phone,
                    '<MISSING>',
                    lat,
                    lon,
                    hours_of_op
                ])
                count += 1
                logger.info(count)
            except:
                pass


    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()