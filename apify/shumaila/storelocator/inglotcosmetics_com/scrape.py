import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chrome_path = '/Users/Dell/local/chromedriver'
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
    url = 'https://inglotcosmetics.com/stores'
   # page = requests.get(url)
    driver = get_driver()
    driver.get(url)
    time.sleep(4)
    hreflist = driver.find_element_by_xpath("/html/body/div[2]/div/div/div[2]/div/div[2]/ul")
    hrefs = hreflist.find_elements_by_tag_name('li')

    print(len(hrefs))
    for n in range(0,len(hrefs)):
        try:
            ccode = str(hrefs[n].find_element_by_class_name('loc-country').text)
            #print(ccode)
        except:
            ccode = "None"
        if ccode.find("USA") > -1:
            gmap = hrefs[n].get_attribute("data-gmapping")[0:110]
            #print(gmap)
            start = 0
            start = gmap.find("id")
            start = gmap.find(":", start) + 2
            end = gmap.find('"', start)
            store = gmap[start:end]
            #print(start)
            start = gmap.find("lat")
            start = gmap.find(":", start) + 2
            end = gmap.find('"', start)
            lat = gmap[start:end]
            start = gmap.find("lng")
            start = gmap.find(":", start) + 2
            end = gmap.find('"', start)
            longt = gmap[start:end]
            title = hrefs[n].find_element_by_class_name('loc-name').text
            address = hrefs[n].find_element_by_class_name('loc-addr').text
            address = address.replace("\n", " ")
            address = usaddress.parse(address)
            print(address)
            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if temp[1].find("Address") != -1 or temp[1].find("Street") != -1 or temp[1].find("Recipient") != -1 or \
                        temp[1].find("BuildingName") != -1 or temp[1].find("USPSBoxType") != -1 or temp[1].find(
                        "USPSBoxID") != -1:
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1

            if len(state) < 2 and len(city) < 3 and len(pcode) < 3:
                street = "<MISSING>"
                temp = address[0]
                city = temp[0]
                temp = address[1] + address[2]
                state = temp[0]
                temp = address[3]
                pcode = temp[0]
            street = street.lstrip()
            city = city.lstrip()
            state = state.lstrip()
            pcode = pcode.lstrip()
            pcode = pcode.replace(",", "")
            print(store)
            print(title)
            print(street)
            print(city)
            print(state)
            print(pcode)
            print(ccode)
            print(lat)
            print(longt)

            if len(state) < 2 and city.find("Washington") > -1:
                state = "WA"
                city = "<MISSING>"
            if len(state) < 2:
                state = "<MISSING>"

            print(".....................")

            data.append([
                    url,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    "<MISSING>",
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
