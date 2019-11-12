import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    lon = re.findall(r'\%2C(--?[\d\.]*)', url)[0]
    lat = re.findall(r'addr=(-?[\d\.]*)', url)[0]
    return lat,lon

def fetch_data():
    data=[]; page_url=[];hours_of_operation=[];location_name=[];links=[];countries=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('https://www.speedycash.com/find-a-store/')
    time.sleep(3)
    stores=driver.find_elements_by_xpath("//a[contains(@href,'/loans/')]")
    stores_href=[stores[n].get_attribute('href').split("/loans")[1] for n in range(0,len(stores))]
    for n in range(1,len(stores_href)):
        url = "https://www.speedycash.com/find-a-store%s"%stores_href[n]
        driver.get(url)
        address = driver.find_elements_by_tag_name('address')
        loc = driver.find_elements_by_link_text('Directions')
        phones = driver.find_elements_by_xpath("//a[contains(@class,'store-phone')]")
        hours = driver.find_elements_by_xpath("//div[@class='row']")
        hour = [hours[n].text for n in range(0,len(hours))]
        for n in range(0,len(address)):
            a=address[n].text.split("\n")
            street_address.append(' '.join(address[n].text.split("\n")[:-1]))
            lat,lon = parse_geo(loc[n].get_attribute('href'))
            latitude.append(lat)
            longitude.append(lon)
            city.append(a[-1].split(",")[0])
            state.append(a[-1].split(",")[1].split()[0])
            zipcode.append(a[-1].split(",")[1].split()[1])
            phone.append(phones[n].text)
            page_url.append(url)
            check_hour = ' '.join(hour[n].split("Hours:")[1:]).strip()
            if check_hour !='':
                hours_of_operation.append(check_hour)
            else:
                hours_of_operation.append('<INACCESSIBLE>')
    for n in range(0,len(street_address)):
        data.append([
            'https://www.speedycash.com',
            page_url[n],
            'Speedy Cash',
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
    return data

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
