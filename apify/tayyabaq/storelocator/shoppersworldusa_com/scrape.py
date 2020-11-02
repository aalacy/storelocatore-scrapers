import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow([str(s) for s in row])

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    #Variables
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('http://shoppersworldusa.com/store.html')
    time.sleep(6)
    # Fetch stores
    stores = driver.find_elements_by_class_name("maincontent")
    loc = stores[0].text.split("\n")
    for i in range(0,len(loc)):
        if loc[i]!="" and loc[i]!=" " and 'COMING SOON' not in loc[i]:
            try:
                tagged = usaddress.tag(loc[i].replace('\u2022', ''))[0]
                street_address.append(tagged['AddressNumber']+" "+tagged['StreetName']+" "+tagged['StreetNamePostType'])
            except:
                try:
                    tagged = usaddress.tag(str(loc[i].replace('\u2022', '').split(",")[1:].join()))[0]
                    street_address.append(tagged['AddressNumber']+" "+tagged['StreetName']+" "+tagged['StreetNamePostType'])
                except:
                    if len(loc[i].split(","))==4:
                        if re.search(r'\d', loc[i].split(",")[1]):
                            street_address.append(loc[i].split(",")[1].strip())
                        else:
                            street_address.append(loc[i].split(",")[0].strip())
                    elif len(loc[i].split(","))==5:
                        if re.search(r'\d', loc[i].split(",")[2]):
                            street_address.append(loc[i].split(",")[2].strip())
                        else:
                            street_address.append(loc[i].split(",")[1].strip())
                    else:
                        street_address.append(loc[i].split(",")[0].strip())
                
            try:
                zipcode.append(tagged['ZipCode'])
            except:
                zipcode.append('<MISSING>')
            try:
                state.append(tagged['StateName'])
            except:
                state.append('<MISSING>')
            try:
                city.append(tagged['PlaceName'].replace("'",""))
            except:
                city.append('<MISSING>')
            try:
                phone.append(re.findall(r'([(]-?[\d\.]*?.*)',loc[i])[0].split(",")[0])
            except:
                phone.append('<MISSING>')
            try:
                if re.search(r'\d', loc[i].split(",")[-4])==False:
                    location_name.append(loc[i].split(",")[-4])
                else:
                    location_name.append('<MISSING>')
            except:
                location_name.append('<MISSING>')
    for n in range(0,len(street_address)): 
        data.append([
            'https://www.shoppersworldusa.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
    
scrape()
