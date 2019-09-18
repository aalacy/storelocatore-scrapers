import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress
import pandas as pd
    
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
    
    
    
def fetch_data():
        # Your scraper here
        data=[]
        driver.get("https://www.lottehotel.com/global/en/hotel-finder.html")
        time.sleep(10)
        
        text_len=driver.find_elements_by_xpath("(//div[contains(@class,'hotel__content')])")
        print(text_len)
        for i in range(20,22):
            print (i)
            location_name = driver.find_element_by_xpath("(//div[contains(@class,'hotel__content')])["+str(i+1)+"]//*[contains(@class,'hotel__name')]").get_attribute("textContent")
            print("loc name:",location_name)
            raw_address =  driver.find_element_by_xpath("(//div[contains(@class,'hotel__content')])["+str(i+1)+"]/p[contains(@class,'hotel__address')] ").get_attribute("textContent")
            print("loc add:",raw_address)
            if location_name =='LOTTE HOTEL GUAM':
                raw_address = raw_address.replace('<br/>','').replace('LOTTE HOTEL GUAM','')
                print("loc add inside if:", raw_address)
            tagged = usaddress.tag(raw_address)[0]
            print("tagged", tagged)
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                              tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['IntersectionSeparator'] + " " + \
                               tagged['SecondStreetName'] + " " + tagged['SecondStreetNamePostType']
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
                    except:
                        pass
            print("street_addr", street_addr)
            state = tagged['StateName']
            city = tagged['PlaceName']
            zipcode = tagged['ZipCode']
            phone = driver.find_element_by_xpath("(//div[contains(@class,'hotel__content')])["+str(i+1)+"]/p[contains(@class,'hotel__tel')] ").get_attribute("textContent")
            phone = phone.replace('Make a Call' , '')
            print("phone", phone)
            data.append([
                 'lottehotel.com',
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
           
            print(i)
        return data
    
    
def scrape():
        data = fetch_data()
        write_output(data)
    
scrape()
