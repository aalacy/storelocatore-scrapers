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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://wingstogo.com/all-locations")
    time.sleep(5)
    stores = driver.find_elements_by_css_selector('div.view-more > a')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    #print(name)
    for i in range(len(name)):
            driver.get(name[i])
            page_url = name[i]
            time.sleep(5)
            street_addr = driver.find_element_by_css_selector('span.detail-address').text
            if "coming soon" in street_addr.lower():
                continue
            location_name = driver.find_element_by_css_selector('div.loc-details-title').text
            
            state_city_zip = driver.find_element_by_css_selector('span.detail-city').text
            zipcode = state_city_zip.split(" ")[-1]
            state = state_city_zip.split(" ")[-2]
            city = state_city_zip.split(",")[0]
            phone = driver.find_element_by_css_selector('span.detail-phone').text
            hours_of_op = driver.find_element_by_css_selector('div.location-hours').text
            try:
                geomap = driver.find_element_by_css_selector('div.loc-details-map > iframe').get_attribute('src')
                lat, lon = parse_geo(geomap)
            except:
                lat=lon="<MISSING>"
            data.append([
                'https://wingstogo.com/',
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
                lat,
                lon,
                hours_of_op
            ])
            count = count + 1
            print(count)

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
