import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgselenium import SgSelenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import re
import json
import time
from random import randrange
import time
import sgzip
import unicodedata


session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w', newline = "",encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    driver = SgSelenium().firefox()
    driver.get("https://www.la-z-boy.com/storeLocator/storeLocator.jsp")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=["US","CA"])
    MAX_RESULTS = 200
    MAX_DISTANCE = 50
    zip = search.next_zip()
    temp_zip = ""
    while zip:
        try:
            result_coords = []
            # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
            # print('Pulling zipcode  %s...' % (str(zip)))
            WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//input[@id='locator']"))
            if temp_zip == "":
                inputElement = driver.find_element_by_xpath(
                    "//input[@id='locator']")
                inputElement.clear()
                inputElement.send_keys(str(zip))
                inputElement.send_keys(Keys.ENTER)
            else:
                WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath(
                    "//input[@value='" + str(temp_zip) + "']"))
                time.sleep(4)
                try:
                    driver.find_element_by_xpath(
                        "//button[@title='No thanks']").click()
                    WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath(
                        "//input[@value='" + str(temp_zip) + "']"))
                except:
                    pass
                try:
                    inputElement = driver.find_element_by_xpath(
                        "//input[@value='" + str(temp_zip) + "']")
                    inputElement.clear()
                    inputElement.send_keys(str(zip))
                    inputElement.send_keys(Keys.ENTER)
                except:
                    driver.get(
                        "https://www.la-z-boy.com/storeLocator/storeLocator.jsp")
                    temp_zip = ""
            time.sleep(2)
            WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//a[text()='Home']"))
            try:
                soup = BeautifulSoup(driver.page_source, 'lxml')
            except:
                temp_zip = ""
                driver.get(
                    "https://www.la-z-boy.com/storeLocator/storeLocator.jsp")
                continue
            data = []
            for script in soup.find_all("script"):
                if "var __locatorResults" in script.text:
                    # print(script.text.split("var __locatorResults = ")[1])
                    data = json.loads(script.text.split(
                        "var __locatorResults = ")[1])[0]["map"]
                    break
            for store_data in data:
                lat = store_data["lat"]
                lng = store_data["longi"]
                result_coords.append((lat, lng))
                store = []
                if "La-Z-Boy" not in store_data["storename"]:
                    continue
                store.append("https://www.la-z-boy.com")
                store.append(store_data["storename"])
                street_address = ""
                if "address1" in store_data:
                    street_address = street_address + store_data["address1"]
                if "address2" in store_data:
                    street_address = street_address + \
                        " " + store_data["address2"]
                if "address3" in store_data:
                    street_address = street_address + \
                        " " + store_data["address3"]
                if street_address == "":
                    continue
                store.append(street_address)
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["city"]
                             if store_data["city"] else "<MISSING>")
                store.append(store_data["state"]
                             if store_data["state"] else "<MISSING>")
                store.append(store_data["zip"]
                             if store_data["zip"] else "<MISSING>")
                store.append(store_data["country"])
                store.append(store_data["storeID"])
                page_url = ""
                hours = ""
                if store_data["website"]:
                    page_url = "https://www.la-z-boy.com" + \
                        store_data["website"]
                    hours_request = session.get(page_url, headers=headers)
                    hours_soup = BeautifulSoup(hours_request.text, "lxml")
                    if hours_soup.find("a", text=re.compile("Store Hours")):
                        hours_details_request = session.get("https://www.la-z-boy.com" + hours_soup.find(
                            "a", text=re.compile("Store Hours"))["href"], headers=headers)
                        hours_details_soup = BeautifulSoup(
                            hours_details_request.text, "lxml")
                        hours = " ".join(list(hours_details_soup.find(
                            "ul", {"class": "hours"}).stripped_strings))
                store.append(
                    store_data["phone"] if "phone" in store_data and store_data["phone"] else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                store.append(hours if hours else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")
                for i in range(len(store)):
                    if type(store[i]) == str:
                        store[i] = ''.join((c for c in unicodedata.normalize(
                            'NFD', store[i]) if unicodedata.category(c) != 'Mn'))
                store = [x.replace("–", "-") if type(x) ==
                         str else x for x in store]
                store = [x.encode('ascii', 'ignore').decode(
                    'ascii').strip() if type(x) == str else x for x in store]
                # print(store)
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store
            if len(data) < MAX_RESULTS:
                # print("max distance update")
                search.max_distance_update(MAX_DISTANCE)
            elif len(data) == MAX_RESULTS:
                # print("max count update")
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " +
                                str(MAX_RESULTS) + " results")
        except Exception as e:
            # print(e)
            search.max_distance_update(MAX_DISTANCE)
            temp_zip = zip
            zip = search.next_zip()
            continue
        temp_zip = zip
        zip = search.next_zip()
    driver.quit();
    # @AfterSuite
    # public void tearDown() {
    #    driver.quit();
    # }

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
