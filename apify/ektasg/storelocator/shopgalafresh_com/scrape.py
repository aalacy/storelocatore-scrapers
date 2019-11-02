import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
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
    #driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
    driver = webdriver.Chrome("chromedriver", options=options)
    driver.get("https://www.shopgalafresh.com/")
    time.sleep(10)

    driver.find_element_by_xpath("//a[contains(text(),'select')]").click()
    clickElements = driver.find_elements_by_xpath("//button[text()='Choose']")
    length = len(clickElements)
    driver.quit()
    for i in range(length):
        #driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
        driver = webdriver.Chrome("chromedriver", options=options)
        driver.get("https://www.shopgalafresh.com/")
        page_url = "https://www.shopgalafresh.com/"
        time.sleep(10)
        driver.find_element_by_xpath("//a[contains(text(),'select')]").click()
        time.sleep(10)
        driver.find_element_by_xpath("(//button[text()='Choose'])[" + str(i + 1) + "]").click()
        time.sleep(10)
        driver.find_element_by_xpath(
            "//span[contains(text(),'Store Info')][ancestor:: span[@ng-repeat='link in footerCtrl.links']]").click()
        time.sleep(10)
        locname = driver.find_element_by_xpath("//div[@class='branch-name']").text
        streetaddress1 = driver.find_element_by_xpath("//div[@class='branch-address']").text
        hour = driver.find_element_by_xpath("//span[@class='branch-hours']").text
        time.sleep(10)

        phone = driver.find_element_by_xpath("//a[contains(text(),'(')]").text
        city = streetaddress1.split(',')[len(streetaddress1.split(',')) - 1].split(' ')[1]
        zipcode = "<MISSING>"
        country = "USA"
        if (i == 0 or i == 2):
            state = streetaddress1.split(',')[len(streetaddress1.split(',')) - 1].split(' ')[2]
        else:
            city = streetaddress1.split(',')[len(streetaddress1.split(',')) - 2]
            state = streetaddress1.split(',')[len(streetaddress1.split(',')) - 1].split(' ')[1]

        lat = '<MISSING>'
        lng = '<MISSING>'
        streetaddress = streetaddress1.split(',')[0]

        data.append([
            'https://www.shopgalafresh.com/',
            page_url,
            locname,
            streetaddress,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            lng,
            hour
        ])
        driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
    return data


data = scrape()





