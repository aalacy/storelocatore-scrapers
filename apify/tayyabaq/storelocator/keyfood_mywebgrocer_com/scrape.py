import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
                
def parse_geo(url):
    try:
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        lon="<MISSING>"
    try:
        lat = re.findall(r'\=(-?[\d\.]*\,)', url)[0]
    except:
        lat="<MISSING>"
    return lat, lon

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('http://keyfood.mywebgrocer.com/StoreLocator.aspx?s=723953668&g=2d6a1d25-bf8f-4056-8736-269d1b9db7cf&uc=581EF7')
    wait = WebDriverWait(driver, 10)
    men_menu = wait.until(ec.visibility_of_element_located((By.XPATH, "//select[@name='selStates']/option")))
    ActionChains(driver).move_to_element(men_menu).perform()
    state_opt = driver.find_elements_by_xpath("//select[@name='selStates']/option")
    state_options = [state_opt[n].text for n in range(0,len(state_opt))]
    for n in range(1,len(state_options)):
        time.sleep(3)
        print((state_options[n]))
        driver.find_element_by_xpath("//select[@name='selStates']/option[text()='%s']"%state_options[n]).click()
        driver.find_element_by_xpath("//select[@name='selZipCodeRadius']/option[text()='20 Miles']").click()
        driver.find_element_by_class_name('submitButton').click()
        location = driver.find_elements_by_class_name('StoreTitle')
        for n in range(0,len(location)):
            location_name.append(location[n].text)
        time.sleep(3)
        lat_lon = driver.find_elements_by_class_name('SingleItemLinkText')
        for n in range(0,len(lat_lon)):
            lat,lon = parse_geo(lat_lon[n].get_attribute('href'))
            latitude.append(lat)
            longitude.append(lon)
        address2=driver.find_elements_by_xpath("//div[@class='StoreAddress']/p[2]")
        address1 = driver.find_elements_by_xpath("//div[@class='StoreAddress']/p[1]")
        for n in range(0,len(address1)):
            street_address.append(address1[n].text)
        for n in range(0,len(address2)):
            city.append(address2[n].text.split(",")[0])
            state.append(address2[n].text.split(",")[1].split()[0])
            zipcode.append(address2[n].text.split(",")[1].split()[1])
        hours = driver.find_elements_by_class_name('StoreHours')
        for n in range(0,len(hours)):
            hours_of_operation.append(hours[n].text)
        phones = driver.find_elements_by_xpath("//div[@class='StoreContact']")
        for n in range(0,len(phones)):
            try:
                phone.append(phones[n].text.split("Phone: ")[1].split("\n")[0])
            except:
                phone.append("<MISSING>")
    for n in range(0,len(location_name)):
        data.append([
            'http://keyfood.mywebgrocer.com',
            location_name[n],
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
