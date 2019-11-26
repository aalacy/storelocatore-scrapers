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
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)


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

    driver.get("https://handymarts.com/locations/")
    time.sleep(5)
    stores = driver.find_elements_by_css_selector('div.ll_wrap')
    page_url = "https://handymarts.com/locations/"
    for store in stores:
            location_name= store.find_element_by_css_selector('div.ll_info > h4').text
            store_num = location_name.split("#")[1].split("– ")[0]
            addr = store.find_element_by_css_selector('p.ll_address').text.splitlines()
            street_addr = addr[0]
            zipcode = addr[1].split(" ")[-1]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[1].split(" ")[-2]
            phone ='<MISSING>'
            hours_of_op = store.find_element_by_css_selector('div.ll_details > ul > li > div > span').text
            geomap =store.find_element_by_css_selector('div.ll_actions > a').get_attribute('href')
            driver2.get(geomap)
            time.sleep(10)
            lat,lon = parse_geo(driver2.current_url)
            data.append([
                 'https://handymarts.com/',
                  page_url,
                  location_name,
                  street_addr,
                  city,
                  state,
                  zipcode,
                  'US',
                  store_num,
                  phone,
                  '<MISSING>',
                  lat,
                  lon,
                  hours_of_op
                ])
            count+=1
            print(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
