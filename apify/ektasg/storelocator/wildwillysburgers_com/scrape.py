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
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon

def parse_geo2(url):
        a = re.findall(r'\&center=(-?[\d\.]*,(--?[\d\.]*))', url)[0]
        lat = a[0].split("%2C")[0]
        lon = a[0].split("%2C")[1]
        return lat, lon

def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://www.wildwillysburgers.com/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.location-box.wpb_column.vc_column_container.vc_col-sm-6 > div.vc_column-inner > div.wpb_wrapper > a')
    names = [stores[i].get_attribute('href') for i in range(0,len(stores))]
    location_names = driver.find_elements_by_css_selector('div.location-box.wpb_column.vc_column_container.vc_col-sm-6 > div.vc_column-inner > div.wpb_wrapper > div.wpb_text_column.wpb_content_element.location_title')
    location_name = [location_names[i].text for i in range(0,len(location_names))]
    for i in range(0,len(names)):
        driver.get(names[i])
        time.sleep(5)
        try:
            geomap = driver.find_element_by_css_selector('div.wpb_map_wraper > iframe').get_attribute('data-lazy-src')
            lat,lon = parse_geo(geomap)
            phone = driver.find_element_by_css_selector('div.wpb_text_column.wpb_content_element.red-icons > div > p >a').text
            address = driver.find_element_by_css_selector('div.wpb_text_column.wpb_content_element.red-icons > div > p > strong > a:nth-child(3)').text
            tagged = usaddress.tag(address)[0]
            state = tagged['StateName']
            city = tagged['PlaceName']
            zipcode = tagged['ZipCode']
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                              tagged['StreetNamePostType'].split('\n')[0]
            except:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreType'] + " " + tagged['StreetName']
        except:
            phone = driver.find_element_by_css_selector('section.lemon--section__373c0__fNwDM.u-space-b3.border-color--default__373c0__2oFDT > div > div:nth-child(1) > div > div.lemon--div__373c0__1mboc.arrange-unit__373c0__1piwO.arrange-unit-fill__373c0__17z0h.border-color--default__373c0__2oFDT > p:nth-child(2)').text
            geomap1 = driver.find_element_by_xpath("//img[contains(@src,'googleapis')]").get_attribute('src')
            lat = geomap1.split('center=')[1].split('%2C')[0]
            lon = geomap1.split('center=')[1].split('%2C')[1].split('&')[0]
            street_addr = driver.find_element_by_css_selector('address.lemon--address__373c0__2sPac > p:nth-child(1) > span').text
            state_city_zip = driver.find_element_by_css_selector('address.lemon--address__373c0__2sPac > p:nth-child(2) > span').text
            city = state_city_zip.split(',')[0]
            zipcode = state_city_zip.split(',')[1].split(" ")[-1]
            state = state_city_zip.split(',')[1].split(" ")[-2]
        data.append([
             'https://www.wildwillysburgers.com/',
              '<MISSING>',
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
              '<MISSING>'
            ])

    i = 0
    while i < len(data):
        data[i][1] = location_name[i]
        i += 1

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()