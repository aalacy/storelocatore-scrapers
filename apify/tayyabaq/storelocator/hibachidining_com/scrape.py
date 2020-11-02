import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)
def parse_geo(url):
    lon = re.findall(r'\,(-=?[\d\.]*)', url)[0]
    lat = re.findall(r'\=(-?[\d\.]*),', url)[0]
    return lat, lon
def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('http://hibachidining.com/website/')
    stores=driver.find_elements_by_xpath("//p[contains(@class,'trigger')]/a")
    location_name = [stores[n].text for n in range(0,len(stores))]
    loc=driver.find_elements_by_xpath("//a[contains(@href,'http://www.google.com/maps')]")
    for n in range(0,len(stores)):
        time.sleep(2)
        stores[n].click()
    time.sleep(3)
    moreinfo = driver.find_elements_by_link_text('More info')
    moreinfo_links = [moreinfo[n].get_attribute('href') for n in range(0,len(moreinfo))]
    address=driver.find_elements_by_xpath("//div[@class='block']")
    for n in range(0,len(address)):
        a=address[n].text.replace('\u2022',"").split("\n")
        if a[-4] not in street_address:
            street_address.append(a[-4])
            city.append(a[-3].split(",")[0])
            state.append(a[-3].split(",")[1].split()[0].strip())
            if 'directions' in a[-3].split(",")[1].split()[1].strip():
                zipcode.append('<MISSING>')
            else:
                zipcode.append(a[-3].split(",")[1].split()[1].strip())
            phone.append(a[-2].replace("."," "))
            lat,lon = parse_geo(loc[n].get_attribute('href'))
            latitude.append(lat)
            longitude.append(lon)
    for n in range(0,len(moreinfo)):
        driver.get(moreinfo_links[n])
        hours_of_operation.append(driver.find_elements_by_id('hours')[1].text)
    for n in range(0,len(street_address)): 
        data.append([
            'http://hibachidining.com',
            '<MISSING>',
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
