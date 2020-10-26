import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import json

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    data = []
    driver.get("https://fitnesstogether.com/personal-trainers-near-me")
    time.sleep(10)

    CountryCodes = driver.find_elements_by_xpath("//a[@class='abbr']")
    Urls = [CountryCodes[i].get_attribute('href') for i in range(0,len(CountryCodes))]
    for i in range(0,len(Urls)):
        driver.get(Urls[i])
        time.sleep(10)
        stores = driver.find_elements_by_xpath("//p[@class='store-address']")
        for i in range(0, len(stores)):
            url = driver.find_element_by_xpath(
                "(//p[@class='store-details']//*[@itemprop='url'])[" + str(i + 1) + "]").get_attribute("href")
            driver2.get(url)
            time.sleep(15)
            try:
                hours_of_op = driver2.find_element_by_xpath("//p[child::em[contains(text(),'Hours of Operation')]]").get_attribute(
                    "textContent").split('Operation')[1].strip().replace("\t", "").replace("\n", "").replace("\xa0", ":")
            except:
                hours_of_op = '<MISSING>'
            text = driver2.find_element_by_xpath("//script[preceding-sibling::main][1]").get_attribute("innerHTML").split(
                "window.mapLocations")[1][2:-2]
            req_json = json.loads(text)
            store_id = req_json[0]['account_number']
            loc_name = req_json[0]['name']
            print(loc_name)
            street_addr = req_json[0]['address']
            city = req_json[0]['city']
            state = req_json[0]['state']
            zipcode = req_json[0]['zip_code']
            phone = req_json[0]['phone_number']

            loc_type = req_json[0]['location_type']
            lat = req_json[0]['latitude']
            lon = req_json[0]['longitude']
            data.append([
                    'https://fitnesstogether.com/',
                    loc_name,
                    street_addr,
                    city,
                    state,
                    zipcode,
                    'US',
                    store_id,
                    phone,
                    loc_type,
                    lat,
                    lon,
                    hours_of_op
                ])

    data1=[]
    for i in range(0,len(data)):
        if data[i][7] not in data1:
            data1.append(data[i])

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data1


def scrape():
    data = fetch_data()
    write_output(data)

scrape()



