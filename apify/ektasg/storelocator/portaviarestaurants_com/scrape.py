import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress


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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://portaviarestaurants.com/")
    time.sleep(10)
    stores = driver.find_elements_by_link_text('Visit Us')
    names = [stores[i].get_attribute('href') for i in range(0,len(stores))]
    for i in range(0,len(names)):
        driver.get(names[i])
        time.sleep(5)
        location_name = driver.find_element_by_css_selector('#content > div > div > div > div > section.elementor-element.elementor-element-d15c9e5.elementor-section-height-min-height.elementor-section-boxed.elementor-section-height-default.elementor-section-items-middle.elementor-section.elementor-top-section > div.elementor-container.elementor-column-gap-default > div > div > div > div > div.elementor-element.elementor-element-366413c.elementor-widget.elementor-widget-heading > div > h2').text
        phone  = driver.find_element_by_xpath("//a[contains(@href,'tel:')]").text
        raw_address = driver.find_element_by_xpath("//a[contains(@href,'goo.gl/maps')]").text
        tagged = usaddress.tag(raw_address)[0]
        street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
        city = tagged['PlaceName']
        state = tagged['StateName']
        zipcode = tagged['ZipCode']
        if i ==0:
            hours_of_op = driver.find_element_by_css_selector('#page > div.elementor.elementor-1280.elementor-location-footer > div > div > section.elementor-element.elementor-element-74c76443.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default.elementor-section.elementor-top-section > div > div > div.elementor-element.elementor-element-af32eb2.elementor-column.elementor-col-33.elementor-top-column > div > div').text
        elif i==1:
            hours_of_op = driver.find_element_by_css_selector('#page > div.elementor.elementor-357.elementor-location-footer > div > div > section.elementor-element.elementor-element-7f46777.elementor-section-boxed.elementor-section-height-default.elementor-section-height-default.elementor-section.elementor-top-section > div > div > div.elementor-element.elementor-element-9ba3bad.elementor-column.elementor-col-33.elementor-top-column > div > div').text
        data.append([
             'https://portaviarestaurants.com/',
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
              hours_of_op
            ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()