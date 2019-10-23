import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
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
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    driver = get_driver()
    driver.get('https://www.gucci.com/us/en/store')
    time.sleep(3)
    driver.find_element_by_xpath("//select[@id='country']/option[text()='United States']").click()
    driver.find_element_by_xpath("//button[@class='js-changecountrygo button-short']").click()
    driver.get('https://www.gucci.com/us/en/store')
    location = driver.find_elements_by_xpath('//h3[@class="name"]/a')
    location_name = [location[n].text for n in range(0,len(location))]
    lat_lon = driver.find_elements_by_xpath('//ol[@id="stores"]/li')
    for n in range(0,len(lat_lon)):
        latitude.append(lat_lon[n].get_attribute('data-latitude'))
        longitude.append(lat_lon[n].get_attribute('data-longitude'))
    address = driver.find_elements_by_class_name('address')
    street_address=[address[n].text.split("\n")[0] for n in range(0,len(address))]
    zipcode = [address[n].text.split("\n")[1].split(",")[-2] for n in range(0,len(address))]
    country = [address[n].text.split("\n")[1].split(",")[-1] for n in range(0,len(address))]
    city = [address[n].text.split("\n")[1].split(",")[0] for n in range(0,len(address))]
    for n in range(0,len(address)):
        a=address[n].text.split("\n")[1].split(",")[1].strip()
        if bool(re.match('^[0-9]+$',str(a)))==True:
            state.append('<MISSING>')
        else:
            state.append(a)
    info = driver.find_elements_by_xpath('//div[@class="store-infos"]')
    phones = driver.find_elements_by_xpath('//div[@class="store-infos"]/div[1]')
    for n in range(0,len(info)):
        if "T:" in info[n].text:
            try:
                phone.append(phones[n].text.split("T:")[1])
            except:
                phone.append('<MISSING>')
        else:
            phone.append('<MISSING>')
    for n in ranrge(0,len(street_address)): 
        data.append([
            'https://www.gucci.com',
            'https://www.gucci.com/us/en/store',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            country[n],
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
