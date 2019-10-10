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
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def parse_geo(url):
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    count=0
    driver.get("https://jumpingworldusa.com/locations/")
    time.sleep(10)

    stores = driver.find_elements_by_css_selector('h2.staff-entry-title.entry-title > a')
    names = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    location_name = [stores[i].text for i in range(0, len(stores))]
    for j in range(0,len(names)):
        print("URL..........." , names[j])
        if 'coming-soon' in names[j]:
            pass
        else:
            driver2.get(names[j])
            time.sleep(5)
            page_url = names[j]
            #location_name = driver2.find_element_by_css_selector('h1.vcex-module.vcex-heading.vcex-heading-plain > span.vcex-heading-inner.clr').text.replace('\n', ' ').replace(',',' ')
            print("location_name" , location_name[j])
            address = driver2.find_element_by_xpath("//a[contains(@href,'https://goo.gl/maps/')]").text
            tagged = usaddress.tag(address)[0]
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                              tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['OccupancyType'] + " " + \
                              tagged['OccupancyIdentifier'].split('\n')[0]
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                  tagged['StreetNamePostType'].split('\n')[0] + " " +\
                                  tagged['OccupancyIdentifier'].split('\n')[0]
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
                                              tagged['StreetNamePostDirectional'].split('\n')[0]
                            except:
                                try:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                  tagged['StreetNamePostType'].split('\n')[0]
                                except:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + \
                                                  tagged['StreetNamePreType'] + " " + tagged['StreetName']
            city = tagged['PlaceName']
            state = tagged['StateName']
            zipcode = tagged['ZipCode']
            phone = driver2.find_element_by_xpath("//a[contains(@href, 'tel:')]").text
            hours_of_op = driver2.find_element_by_css_selector('table.table-hours').text
            geomap = driver2.find_element_by_xpath("//iframe[contains(@src,'https://www.google.com/maps/')]").get_attribute('src')
            lat,lon = parse_geo(geomap)
            data.append([
                 'https://jumpingworldusa.com/',
                  page_url,
                  location_name[j],
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
            print(count)

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()