import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver=get_driver()
    driver.get('https://www.thenomadhotel.com')
    time.sleep(8)
    locations= driver.find_elements_by_xpath("//ul[@class='city-selector']/li/a")
    location = [locations[n].get_attribute('href') for n in range(0,len(locations))]
    time.sleep(3)
    for n in range(0,len(location)-1):
        driver.get(location[n])
        time.sleep(12)
        try:
            location_name.append(driver.find_element_by_class_name("name").text)
            address = driver.find_element_by_class_name("address-link-wrapper").text
            street_address.append(address.split("\n")[0])
            city.append(address.split("\n")[1].split(",")[0])
            state.append(address.split("\n")[1].split(",")[1].split()[0])
            zipcode.append(address.split("\n")[1].split(",")[1].split()[1])
            phone.append(driver.find_element_by_class_name("phone").text)
        except:
            try:
                location_name.append(driver.find_element_by_class_name("title").text)
                address = driver.find_element_by_class_name("address-link-wrapper")
                street_address.append(driver.find_element_by_xpath("//span[@class='address1'][2]").text)
                city.append(driver.find_element_by_class_name("city").text)
                st = driver.find_element_by_class_name("state").text
                if st==[] or st=="":
                    state.append('<MISSING>')
                else:
                    state.append(st)
                zipcode.append(driver.find_element_by_class_name("zip").text)        
            except:
                address = driver.find_elements_by_xpath("//div[@class='main-address']/div/p")
                location_name.append(address[0].text)
                street_address.append(address[-3].text)
                try:
                    city.append(address[-2].text.split(",")[0])
                    state.append(address[-2].text.split(",")[1].split()[0])
                    zipcode.append(address[-2].text.split(",")[1].split()[1])
                except:
                    a=address[-2].text.split()[1:2]
                    city.append(' '.join(a))
                    state.append(address[-2].text.split()[-2])
                    zipcode.append(address[-2].text.split()[-1])
            try:
                phone.append(address[-1].text)
            except:
                try:
                    phone.append(driver.find_element_by_class_name("phone").text)
                except:
                    phone.append("<MISSING>")
    for n in range(0,len(location_name)):
        data.append([
            'https://www.thenomadhotel.com',
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
