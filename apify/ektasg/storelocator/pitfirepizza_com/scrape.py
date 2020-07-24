import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-plugins")
options.add_argument("--no-experiments")
options.add_argument("--disk-cache-dir=null")

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
    driver.get("http://www.pitfirepizza.com/contact")
    time.sleep(10)
    l1 = driver.find_element_by_xpath(
        "//span[text()='PITFIRE LOCATIONS']/../following-sibling::span/span/span").get_attribute("textContent")
    l1 = l1.split('MAP + DIRECTIONS')
    l1 = [k.strip() for k in l1]
    name = [j.split("\n") for j in l1]
    #print(len(name) )
    name[5].remove('SUITE 3')
    for i in range(len(name) - 1):
        #print(name[i])
        location_name = name[i][0]
        street_address = name[i][1]
        state = name[i][2].split(" ")[len(name[i][2].split(" ")) - 2]
        zipcode = name[i][2].split(" ")[len(name[i][2].split(" ")) - 1]
        city = name[i][2].split(" ")[:len(name[i][2].split(" ")) - 2]
        if (len(city) == 1):
            city=city[0]
        else:
            city = name[i][2].split(" ")[:len(name[i][2].split(" ")) - 2][0] + " " + \
                   name[i][2].split(" ")[:len(name[i][2].split(" ")) - 2][1]
        phone = name[i][3].split(" ")[1]
        try:
            hours_of_operation = name[i][4] + " " + name[i][5]
        except:
            hours_of_operation = name[i][4]
        country = 'US'
        data.append([
            'www.pitfirepizza.com',
            location_name,
            street_address,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phone,
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            hours_of_operation
        ])

    geomaps = driver.find_elements_by_xpath("//a[contains(@href,'//goo.gl/maps')]")
    geo_url = [geomaps[i].get_attribute('href') for i in range(0, len(data))]
    for i in range(0, len(geo_url)):
        driver2.get(geo_url[i])
        time.sleep(10)
        lat, lon = parse_geo(driver2.current_url)
        data[i][10] = lat
        data[i][11] = lon
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




