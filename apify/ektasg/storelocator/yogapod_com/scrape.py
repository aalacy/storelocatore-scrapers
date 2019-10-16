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
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://www.yogapod.com/studios/")
    time.sleep(5)
    stores = driver.find_elements_by_css_selector('div.textwidget > ul > li > a')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    name = name[:-5]
    for i in range(len(name)):
            driver.get(name[i])
            page_url = name[i]
            print(page_url)
            time.sleep(5)
            location_name = page_url.split(".com/")[1].replace("/","")
            address = driver.find_element_by_xpath("//span[contains(@itemprop,'address')]").text
            tagged = usaddress.tag(address)[0]
            try:
                street_addr = tagged['BuildingName'].split('\n')[0] + " " + tagged['AddressNumber'] + " " + \
                              tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + \
                              tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier']
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged[
                    'StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                      tagged['StreetNamePostType'].split('\n')[0] + " " + tagged[
                                          'StreetNamePostDirectional'] + " " + tagged['OccupancyIdentifier']
                    except:
                        try:
                            street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged[
                                'StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                        except:
                            try:
                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                              tagged['StreetNamePostDirectional'].split('\n')[0] + " " + \
                                              tagged['StreetNamePostType'].split('\n')[0]
                            except:
                                try:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                  tagged['StreetNamePostType'].split('\n')[0] + " " + \
                                                  tagged['OccupancyIdentifier'].split('\n')[0]
                                except:
                                    try:
                                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                      tagged['StreetNamePostType'].split('\n')[0]
                                    except:
                                        try:
                                            street_addr = tagged['AddressNumber'] + " " + tagged[
                                                'StreetNamePreType'] + " " + tagged['StreetName'] + " " + tagged[
                                                              'StreetNamePostDirectional']
                                        except:
                                            try:
                                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
                                            except:
                                                street_addr = '<MISSING>'

            state = tagged['StateName']
            city = tagged['PlaceName']
            zipcode = tagged['ZipCode']
            phone = driver.find_element_by_xpath("//a[contains(@href,'tel:')]").text
            if phone == "" or phone == " ":
                phone = '<MISSING>'
            elements = driver.find_elements_by_css_selector('div.mk-text-block')
            for elem in elements:
                try:
                    h4_elem = elem.find_element_by_css_selector('h4')
                    if h4_elem.text.lower() == 'studio hours':
                        hours = elem.find_elements_by_css_selector('h6')
                        hours_of_op = ""
                        for j in hours:
                            hours_of_op = hours_of_op + j.text
                        break
                except:
                    try:
                        hours_elem = elem.find_element_by_css_selector('table.mabel-bhi-businesshours')
                        hours_of_op = hours_elem.text
                        break
                    except:
                        pass
            if hours_of_op == "" or hours_of_op == " ":
                hours_of_op = '<MISSING>'

            geomap = driver.find_element_by_xpath("//a[contains(@href,'https://goo.gl/maps/')]").get_attribute('href')
            driver2.get(geomap)
            time.sleep(5)
            lat,lon = parse_geo(driver2.current_url)
            data.append([
                'https://www.yogapod.com/',
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