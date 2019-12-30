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
#chrome_path = '/Users/Dell/local/chromedriver'
driver = webdriver.Chrome('chromedriver', options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain",'page_url', "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("http://beefsteakveggies.com/where-we-are/")
    globalvar = driver.execute_script("return locations;")
    i = 0
    stores = driver.find_elements_by_css_selector('div.contact-box')
    for store in stores:
        location_name = store.find_element_by_css_selector('h2.contact-title').text
        address = store.find_element_by_tag_name('address').find_element_by_tag_name('p').text
        start = address.find('At the corner')
        address = address[0:start]
        if address.find('food truck') == -1:
            address = usaddress.parse(address)
            m = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while m < len(address):
                temp = address[m]                
                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                    "USPSBoxID") != -1:
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]                    
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                
                m += 1
        else:
            street = '<MISSING>'
            city = '<MISSING>'
            state = '<MISSING>'
            pcode = '<MISSING>'
            
        street = street.lstrip()
        city = street.lstrip()
        state = state.lstrip()
        pcode = pcode.lstrip()
            
        if city.find("Building") > -1:
            street = street + " " + city            
            city,state = state.split(' ',1)
        try:
            if city == street:                  
                city,state = state.split(' ',1)
        except:
            pass
        try:
            phone = store.find_element_by_css_selector('div.contact-info').text
            
            phone = phone.replace('CONTACT US','')
            phone = phone.replace('email us','')            
            if len(phone) < 3:
                phone = '<MISSING>'
        except:
            phone = '<MISSING>'
        phone= phone.replace('\n','')
        #print(phone)
        latitude = globalvar[i]['lat_lng'].split(',')[0]
        longitude = globalvar[i]['lat_lng'].split(',')[1]
        store_id = globalvar[i]['marker_id']
        hours_of_op = store.find_element_by_css_selector('div.contact-timing').text       
        hours_of_op = hours_of_op.replace('Hours of Operation:','')       
        hours_of_op = hours_of_op.replace('HOURS','')
        hours_of_op = hours_of_op.replace('LEARN MORE','')
        hours_of_op = hours_of_op.replace('\n',' ')
        hours_of_op = hours_of_op.lstrip()
        street = street.replace('\n',' ')
        data.append([
             'http://beefsteakveggies.com/',
             'http://beefsteakveggies.com/where-we-are/',
              location_name,
              street,
              city,
              state,
              pcode,             
              'US',
              store_id,
              phone,
              '<MISSING>',
              latitude,
              longitude,
              hours_of_op
            ])
        #print(data[i])
        i+=1

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
