import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress
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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
# Your scraper here

def parse_geo(url):
    a=re.findall(r'll=(-?[\d\.]*,(--?[\d\.]*))',url)[0]
    lat = a[0].split(",")[0]
    lon = a[0].split(",")[1]
    return lat, lon

def fetch_data():

    data=[]
    driver.get("https://www.luckyssteakhouse.com/)")
    time.sleep(10)

    lucky_brands=driver.find_elements_by_xpath("//ul[contains(@class,'luckys-brands')]//a")
    li_url = [lucky_brands[i].get_attribute('href') for i in range(0,len(lucky_brands))]

    li_url2=li_url[1:]
    driver.get(li_url[0])
    time.sleep(10)
    steak_stores=driver.find_elements_by_xpath("//div//a[text()='Learn More']")
    for j in steak_stores:
        li_url2.append(j.get_attribute('href'))
        
    for i in range(len(li_url2)):
        driver.get(li_url2[i])
        time.sleep(10)
        print(i)
        hours_of_op = driver.find_element_by_xpath("//p[strong[not(contains(text(),'Keep'))]]").get_attribute("textContent").replace('\t','').replace('\n','')
        try:
            phone_no = driver.find_element_by_xpath("(//h2//a)").get_attribute("textContent")
        except:
            phone_no = '<MISSING>'
        raw_address = driver.find_element_by_xpath("(//h3[contains(@class,'pattern')])").get_attribute("textContent")
        store_name = driver.find_element_by_xpath("//title").get_attribute("textContent")
        try:
            geomap = driver.find_element_by_xpath("//a[contains(@href, 'maps.google.com')]").get_attribute('href')
            lat,lng = parse_geo(geomap)
        except:
            lat = '<MISSING>'
            lng = '<MISSING>'
        try:
            tagged = usaddress.tag(raw_address)[0]
        except:
            pass
        try:
            street_addr = tagged['BuildingName'] + " "+ tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
        except:
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0] + " " +tagged['StreetNamePostType'].split('\n')[0]
                    except:
                        try:
                            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0]
                        except:
                            try:
                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                            except:
                                try:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
                                except:
                                    pass
            try:
                state = tagged['StateName']
                city = tagged['PlaceName']
                zipcode = tagged['ZipCode']
            except:
                pass
        data.append([
         'https://www.luckyssteakhouse.com/',
          store_name,
          street_addr,
          city,
          state,
          zipcode,
          'US',
          '<MISSING>',
          phone_no,
          '<MISSING>',
          lat,
          lng,
          hours_of_op
        ])
    time.sleep(3)
    driver.quit()
    return data
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


    
    
    
    
    
    



