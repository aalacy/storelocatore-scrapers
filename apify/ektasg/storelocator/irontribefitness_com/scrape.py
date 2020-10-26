import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('irontribefitness_com')




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
    a=re.findall(r'\?ll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    count=0
    driver.get("https://www.irontribefitness.com/locations/")
    time.sleep(10)

    stores = driver.find_elements_by_css_selector('a.btn.btn-blue.tiny')
    names = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    page = 2
    while True:
        if len(driver.find_elements_by_xpath("//a[text()='Next ']")) > 0:
            next_page = "https://www.irontribefitness.com/locations/page/{}/".format(page)
            driver.get(next_page)
            time.sleep(10)
            try:
                stores = driver.find_elements_by_css_selector('a.btn.btn-blue.tiny')
                for i in range(0,len(stores)):
                    names.append(stores[i].get_attribute('href'))
                page+=1
            except:
                break
        else:
            break
    for j in range(0,len(names)):
                logger.info("URL..........." , names[j])
                driver2.get(names[j])
                time.sleep(5)
                page_url = names[j]
                location_name = driver2.find_element_by_css_selector('div.location-title > h1').text
                logger.info("location_name" , location_name)
                address = driver2.find_element_by_css_selector('div.col.span_1_of_3.sidebar > p:nth-child(2)').text
                try:
                    tagged = usaddress.tag(address)[0]
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                      tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['OccupancyType'] + " " + \
                                      tagged['OccupancyIdentifier'].split('\n')[0]
                    except:
                        try:
                            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                          tagged['StreetNamePostType'].split('\n')[0] + " " + \
                                          tagged['OccupancyIdentifier'].split('\n')[0]
                        except:
                            try:
                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + \
                                              tagged[
                                                  'StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                            except:
                                try:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                  tagged['StreetNamePostDirectional'].split('\n')[0] + " " + \
                                                  tagged['StreetNamePostType'].split('\n')[0]
                                except:
                                    try:
                                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                      tagged['StreetNamePostDirectional'].split('\n')[0]
                                    except:
                                        try:
                                            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                          tagged['StreetNamePostType'].split('\n')[0]
                                        except:
                                            try:
                                                street_addr = tagged['AddressNumber'] + " " + tagged[
                                                    'StreetNamePreDirectional'] + " " + \
                                                              tagged['StreetNamePreType'] + " " + tagged['StreetName']
                                            except:
                                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'].split('\n')[0]
                    city = tagged['PlaceName']
                    state = tagged['StateName']
                    zipcode = tagged['ZipCode']
                except:
                    zipcode = address.split(" ")[-1]
                    state = address.split(" ")[-2]
                    city = address.split(" ")[-3]
                    street_addr = address.split(",")[0].replace(city, '')
                phone = driver2.find_element_by_xpath("//a[contains(@href, 'tel:')]").text
                store_id = driver2.find_element_by_xpath("//link[contains(@rel, 'shortlink')]").get_attribute('href').split('p=')[1]
                try:
                    geomap = driver2.find_element_by_xpath("//a[contains(@href,'https://maps.google.com/maps?ll=')]").get_attribute('href')
                    lat,lon = parse_geo(geomap)
                except:
                    lat = '<MISSING>'
                    lon = '<MISSING>'
                data.append([
                     'https://www.irontribefitness.com/',
                      page_url,
                      location_name,
                      street_addr,
                      city,
                      state,
                      zipcode,
                      'US',
                      store_id,
                      phone,
                      '<MISSING>',
                      lat,
                      lon,
                      '<MISSING>'
                    ])
                count+=1
                logger.info(count)


    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()