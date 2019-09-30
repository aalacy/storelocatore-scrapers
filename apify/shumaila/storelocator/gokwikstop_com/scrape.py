import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys



def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chrome_path = '/Users/Dell/local/chromedriver'
    #return webdriver.Chrome(chrome_path, chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'https://gokwikstop.com/store-locator/'
    driver = get_driver()
    driver.get(url)
    option = driver.find_element_by_xpath("//div[@id='wpsl-stores']/ul")
    listt = option.find_elements_by_css_selector('li')


    for llist in listt:
        store = llist.get_attribute('data-store-id')
        detail = llist.text
        detail = detail.replace("\n","|")
        print(store)
        print(detail)
        start = 0
        end = detail.find("|",start)
        title = detail[start:end]
        start = end + 1
        end = detail.find("|", start)
        street = detail[start:end]
        start = end + 1
        end = detail.find(" ", start)
        city = detail[start:end]
        start = end + 1
        end = detail.find(" ", start)
        state = detail[start:end]
        start = end + 1
        end = detail.find("|", start)
        pcode = detail[start:end]
        address = street + "," + city + "," + state
        address = address.replace(" ","+")
        link = 'https://www.google.com/maps/dir//' + address
        browser = get_driver()
        browser.get(link)
        time.sleep(3)
        link = browser.current_url
        #print(browser.current_url)
        start = link.find("@")
        if start != -1:
            end = link.find(",",start)
            lat = link[start+1:end]
            start = end + 1
            end = link.find(",", start)
            longt = link[start:end]
        else:
            lat = "<MISSING>"
            longt = "<MISSING>"
        browser.quit()

        print(lat)
        print(longt)
        print("......................................")

        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            store,
            "<INACCESSIBLE>",
            "<MISSING>",
            lat,
            longt,
            "<MISSING>"
        ])
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
