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
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    try:
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        lon = url.split("/@")[1].split(",")[1].split(",")[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    count=0

    driver.get("http://davisoil.net/locations/")
    time.sleep(5)
    stores = driver.find_elements_by_css_selector('div.entry-content > p')
    page_url = "http://davisoil.net/locations/"
    for store in stores:
        info = store.text.splitlines()
        location_name= info[0]
        street_addr = info[1]
        state = info[2].split(",")[1]
        city = info[2].split(",")[0]
        zipcode = info[2].split(",")[2]
        phone = info[3]
        data.append([
                 'http://davisoil.net/',
                  page_url,
                  location_name,
                  street_addr,
                  city,
                  state,
                  zipcode,
                  'US',
                  '<MISSING>',
                  phone,
                  '<MISSING>',
                  '<MISSING>',
                  '<MISSING>',
                  '<MISSING>'
                ])
        count+=1
        print(count)

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()