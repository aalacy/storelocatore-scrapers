import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://mtmtavern.com/locations-menus/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.location-excerpt > a:nth-child(1)')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    time.sleep(5)
    for i in range(0,len(name)):
        driver.get(name[i])
        page_url = name[i]
        time.sleep(5)
        location_name= driver.find_element_by_id('LbHeading').text
        address = driver.find_element_by_css_selector('span.lb-address').text
        loc_type = '<MISSING>'
        street_addr = address.split(",")[0].replace("\n", " ")
        city = address.split(",")[1]
        state = address.split(",")[2].split(" ")[-2]
        zipcode = address.split(",")[2].split(" ")[-1]
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        phone = driver.find_element_by_xpath("//a[contains(@href,'tel:')]").text
        hours_of_op = driver.find_element_by_id('BusinessHours').text.replace("\n", " ")
        data.append([
                'https://mtmtavern.com/',
                page_url,
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone,
                loc_type,
                latitude,
                longitude,
                hours_of_op
            ])
        count = count + 1
        print(count)

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()