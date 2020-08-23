import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    data = [];
    location_name = [];
    address_stores = [];
    city = [];
    street_address = [];
    zipcode = [];
    state = [];
    lat = [];
    long = [];
    hours_of_operation = [];
    phone = []
    # Driver
    driver = get_driver()
    driver.get('http://www.pinktaco.com/locations/')
    stores = driver.find_elements_by_xpath("//li[@class='location']/a")
    store_text = [stores[n].text for n in range(0, len(stores))]
    store_links = [stores[n].get_attribute('href') for n in range(0, len(stores))]
    coords=re.findall(r'LatLng = \[ *(-?[\d\.]+), *(-?[\d\.]+)\];',str(driver.page_source))
    for n in range(0, len(store_links)):
        if '\nCOMING SOON\n' not in store_text[n]:
            driver.get(store_links[n])
            time.sleep(5)
            loc = driver.find_element_by_xpath("//div[@class='details']/h1[1]").text
            if loc != "LOCATION":
                location_name.append(loc)
            else:
                location_name.append('<MISSING>')
            street_address.append(driver.find_element_by_xpath("//div[@class='details']/p[1]").text.split(",")[0])
            try:
                city.append(driver.find_element_by_xpath("//div[@class='details']/p[1]").text.split(",")[1].strip())
                state.append(
                    driver.find_element_by_xpath("//div[@class='details']/p[1]").text.split(",")[2].split()[0].strip())
                zipcode.append(
                    driver.find_element_by_xpath("//div[@class='details']/p[1]").text.split(",")[2].split()[1].strip())
                phone.append(driver.find_element_by_xpath("//div[@class='details']/p[2]").text)
            except:
                city.append(driver.find_element_by_xpath("//div[@class='details']/p[2]").text.split(",")[0].strip())
                state.append(
                    driver.find_element_by_xpath("//div[@class='details']/p[2]").text.split(",")[1].split()[0].strip())
                zipcode.append(
                    driver.find_element_by_xpath("//div[@class='details']/p[2]").text.split(",")[1].split()[1].strip())
                phone.append(driver.find_element_by_xpath("//div[@class='details']/p[3]").text)
            hours = driver.find_element_by_class_name('details')
            if "RESTAURANT HOURS" in hours.text:
                hours_of_operation.append(
                    hours.text.replace(u'\u2013', ' ').split("RESTAURANT HOURS")[1].strip().split('CHECK')[0].replace(
                        '\n', ' '))

            else:
                hours_of_operation.append("<MISSING>")

            """cs = driver.find_element_by_class_name('map-location').find_elements_by_tag_name('a')
            for a in cs:
                if a.get_attribute('title') == "Open this area in Google Maps (opens a new window)":
                    coord = a.get_attribute('href')
                    lat.append(re.findall(r'll=(-?[\d\.]+),', coord)[0])
                    long.append(re.findall(r'll=-?[\d\.]+,(-?[\d\.]+)', coord)[0])
                    break
            """

            lati,longi= coords[n]

            lat.append(lati)
            long.append(longi)

    for n in range(0, len(location_name)):
        data.append([
            'http://www.pinktaco.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            lat[n],
            long[n],
            hours_of_operation[n]
        ])
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
