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
        writer.writerow(["locator_domain", "page_url","location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
                
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(r'chromedriver', chrome_options=options)

def parse_geo(url):
    try:
        lon = re.findall(r'\,(-=?[\d\.]*)', url)[0]
        lat = re.findall(r'\=(-?[\d\.]*),', url)[0]
    except:
        lon = re.findall(r'\!2d(-?[\d\.]*)', url)[0]
        lat = re.findall(r'\!3d(-?[\d\.]*)!', url)[0]
    return lat,lon
    
def fetch_data():
    data=[];store_no=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('https://www.zenmassageusa.com/find-zen/')
    time.sleep(6)
    address=driver.find_elements_by_xpath("//a[contains(@href,'http://www.zenmassageusa')]")
    street = driver.find_elements_by_xpath("//div[@id='wpsl-stores']/ul/li/div/p")
    links = driver.find_elements_by_xpath('//a[contains(text(), "Zen Massage ")]')
    link = driver.find_element_by_xpath("//main[@id='content']/p[2]").text
    links_href = [links[n].get_attribute("href") for n in range(0,len(links))]
    store = driver.find_elements_by_xpath("//div[@id='wpsl-stores']/ul/li")
    for n in range(0,len(street)):
        try:
            tagged = usaddress.tag(street[n].text)[0]
            city.append(tagged['PlaceName'])
            state.append(tagged['StateName'])
            zipcode.append(tagged['ZipCode'].strip().replace("'",""))
            location_name.append(street[n].text.split("\n")[0])
        except:
            tagged = usaddress.tag(str(street[n].text.split("\n")[2:]))[0]
            city.append(tagged['PlaceName'])
            state.append(tagged['StateName'])
            zipcode.append(tagged['ZipCode'].strip().replace("'",""))
            location_name.append(street[n].text.split("\n")[0])
        store_no.append(store[n].get_attribute("data-store-id"))
        if 'Suite' in street[n].text:
                street_address.append(' '.join(str(street[n].text.split("\n")[1]+', '+street[n].text.split("\n")[2]).split(",")[:2]))
        else:
                street_address.append(street[n].text.split("\n")[1])
    for n in range(0,len(links_href)-1):
        driver.get(links_href[n])
        time.sleep(2)
        phone.append(driver.find_element_by_xpath("//a[contains(@href,'tel')]").get_attribute("href").split("tel:")[1])
        hours_of_operation.append(driver.find_element_by_xpath("//div[contains(@class,'tt-column')]").text.split("Hours of Operation")[-1].replace(":","").strip().replace("\n"," "))
        url = driver.find_element_by_xpath("//iframe[contains(@src,'google')]")
        lat,lon=parse_geo(url.get_attribute('src'))
        latitude.append(lat)
        longitude.append(lon)
    location_name.append(link)
    state.append("<MISSING>")
    city.append("<MISSING>")
    zipcode.append("<MISSING>")
    street_address.append("<MISSING>")
    phone.append("<MISSING>")
    phone.append("<MISSING>")
    hours_of_operation.append("<MISSING>")
    store_no.append("<MISSING>")
    latitude.append("<MISSING>")
    longitude.append("<MISSING>")
    for n in range(0,len(location_name)):
        data.append([
            'https://www.zenmassageusa.com/',
            links_href[n],
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            store_no[n],
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
