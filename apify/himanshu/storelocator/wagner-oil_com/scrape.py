import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import time
import html
import platform
system = platform.system()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if "linux" in system.lower():
        return webdriver.Firefox(executable_path='./geckodriver', options=options)

    else:
        # return webdriver.Firefox(executable_path='/usr/local/Cellar/geckodriver/0.26.0/bin/geckodriver', options=options)
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)


def fetch_data():
    # pass
    r = requests.get("http://www.wagner-oil.com/store-locator/")
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())
    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
    phone_tag = []
    city_tag = []
    k = (soup.find('table'))
    for i in k.find_all('tr'):
        data = (list(i.stripped_strings))
        # print(data)
        # print(len(data))
        # print('~~~~~~~~~~~~')
        if len(data) == 4:
            phone_tag.append(data[3])
            city_tag.append(data[0])

    iframe_link = soup.find("iframe")["src"]
    r = requests.get(iframe_link)
    soup = BeautifulSoup(r.text, "lxml")
    # geo_location = {}
    l1 = []
    l2 = []
    for script in soup.find_all("script"):
        if "_pageData" in script.text:
            location_list = json.loads(script.text.split('var _pageData = "')[1].split('\n";')[0].replace(
                '\\"', '"').replace(r"\n", "")[:-2].replace("\\", " "))[1][6]  # [0][12][0][13][0]
            for state in location_list:
                locations = state[4]
                for location in locations:
                    # geo_location[location[5][0][0].replace(
                    #     " u0027s", "'s")] = location[4][0][1]

                    l1.append(location[4][0][1][0])
                    l2.append(location[4][0][1][-1])

    driver = get_driver()
    addresses = []
    driver.get(iframe_link)
    time.sleep(3)
    driver.find_element_by_xpath(
        "//div[@class='i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c']").click()
    for button in driver.find_elements_by_xpath("//*[contains(text(), '...')]"):
        time.sleep(3)
        button.click()
    for button in driver.find_elements_by_xpath("//div[contains(@index, '')]"):
        try:
            try:
                driver.find_element_by_xpath(
                    "//div[@class='U26fgb mUbCce p9Nwte HzV7m-tJHJj-LgbsSe qqvbed-a4fUwd-LgbsSe']").click()
            except:
                pass
            if button.get_attribute("index") == None:
                continue
            time.sleep(3)
            button.click()
            time.sleep(4)
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            # print(location_soup.prettify())
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
            street_address = list(location_soup.find(
                "div", text=re.compile("name")).parent.stripped_strings)[1]

            name = list(location_soup.find(
                "div", text=re.compile("description")).parent.stripped_strings)[1]
            address = list(location_soup.find(
                'div', class_='fO2voc-jRmmHf-MZArnb-Q7Zjwb').stripped_strings)
            # if "EE. UU." in " ".join(address):
            #     address.remove(' EE. UU.')
            # if " Stati Uniti" in " ".join(address):
            #     address.remove(' Stati Uniti')
            # if "Spojené státy americké" in " ".join(address):
            #     address.remove(' Spojené státy americké')
            # print(address)
            # print('~~~~~~~~~~~~~~~~~~~~~~~~')

            if city_tag != []:
                city = city_tag.pop(0)
            # state = address[-2].split()[0].strip()
            # store_zip = address[-2].split()[-1].strip()
            store_zip_split = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(address[0:])))
            # print(store_zip_split)
            if store_zip_split:
                store_zip = store_zip_split[-1]
            else:
                store_zip = "<MISSING>"
            state_split = re.findall("([A-Z]{2})", str(" ".join(address[0:])))
            if state_split:
                state = state_split[-1]
            else:
                state = "<MISSING>"
            # print(city + " | " + state + " | " + store_zip)
            if phone_tag != []:
                phone = phone_tag.pop(0)
            if l1 != []:
                latitude = l1.pop(0)
            if l2 != []:
                longitude = l2.pop(0)
            # print(phone)
            # print(latitude, longitude)
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
            store = []
            store.append("http://www.wagner-oil.com")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append('http://www.wagner-oil.com/store-locator/')
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
            #print("data == " + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
            yield store
            time.sleep(5)
            driver.find_element_by_xpath(
                "//div[@class='U26fgb mUbCce p9Nwte HzV7m-tJHJj-LgbsSe qqvbed-a4fUwd-LgbsSe']").click()
        except Exception as e:
            #print(e)
            time.sleep(3)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
