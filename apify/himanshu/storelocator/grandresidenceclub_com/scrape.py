import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
import time
import unicodedata


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




def fetch_data():
    driver = SgSelenium().firefox()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    addresses = []
    brand_id = "FP"
    domain_url = "https://four-points.marriott.com"
    driver.get("https://www.marriott.com/search/submitSearch.mi?showMore=true&marriottBrands=" +
               str(brand_id) + "&destinationAddress.country=US")
    while True:
        element = WebDriverWait(driver, 100).until(
            lambda x: x.find_element_by_xpath("//div[text()='Destination']"))
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "lxml")
        # print(soup.find('div', {'class': 'js-property-list-container'}).prettify())
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        for location in soup.find('div', {'class': 'js-property-list-container'}).find_all("div", {"data-brand": str(brand_id)}, recursive=False):
            if location["data-brand"] != brand_id:
                continue
            name = location.find("span", {"class": "l-property-name"}).text
            address = location.find("div", {"data-address-line1": True})
            street_address = address["data-address-line1"]
            if location.find("div", {"data-address-line2": True}):
                street_address = street_address + \
                    " " + address["data-address-line2"]
            city = address["data-city"]
            state = address["data-state"]
            store_zip = address["data-postal-code"]
            phone = address["data-contact"]
            lat = json.loads(location["data-property"])["lat"]
            lng = json.loads(location["data-property"])["longitude"]
            detail_id = location.find(
                "span", {"class": "l-property-name"}).parent.parent["href"].split("=")[-1]
            # print(detail_id)
            page_url = "https://www.marriott.com/" + str(detail_id)
            # print(page_url)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            store = []
            store.append("https://grandresidenceclub.com")
            store.append(name if name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            if store[-1] == "":
                continue
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(store_zip if store_zip else "<MISSING>")
            if len(store[-1]) == 10:
                store[-1] = store[-1].replace(" ", "-")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone.split(";")[0] if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize(
                        'NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–", "-") if type(x) ==
                     str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
            # print("data ==" + str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

            yield store
        # if len(soup.find('div', {'class': 'js-property-list-container'}).find_all("div", {"data-brand": str(brand_id)})) <= 0:
        #     break
        soup = BeautifulSoup(driver.page_source, "lxml")
        if soup.find("a", {"title": "Next"}):
            driver.find_element_by_xpath("//a[@title='Next']").click()
        else:
            break
    driver.get("https://www.marriott.com/search/submitSearch.mi?showMore=true&marriottBrands=" +
               str(brand_id) + "&destinationAddress.country=CA")
    while True:
        element = WebDriverWait(driver, 100).until(
            lambda x: x.find_element_by_xpath("//div[text()='Destination']"))
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "lxml")
        for location in soup.find('div', {'class': 'js-property-list-container'}).find_all("div", {"data-brand": str(brand_id)}, recursive=False):
            if location["data-brand"] != brand_id:
                continue
            name = location.find("span", {"class": "l-property-name"}).text
            address = location.find("div", {"data-address-line1": True})
            street_address = address["data-address-line1"]
            if location.find("div", {"data-address-line2": True}):
                street_address = street_address + \
                    " " + address["data-address-line2"]
            city = address["data-city"]
            state = address["data-state"]
            store_zip = address["data-postal-code"]
            phone = address["data-contact"]
            lat = json.loads(location["data-property"])["lat"]
            lng = json.loads(location["data-property"])["longitude"]
            detail_id = location.find(
                "span", {"class": "l-property-name"}).parent.parent["href"].split("=")[-1]
            # print(detail_id)
            page_url = "https://www.marriott.com/" + str(detail_id)
            # print(page_url)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
            store = []
            store.append("https://grandresidenceclub.com")
            store.append(name if name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            if store[-1] == "":
                continue
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(store_zip.replace("-", " ")
                         if store_zip else "<MISSING>")
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone.split(";")[0] if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize(
                        'NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–", "-") if type(x) ==
                     str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
            # print("data ==" + str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
        # if len(soup.find('div', {'class': 'js-property-list-container'}).find_all("div", {"data-brand": str(brand_id)})) <= 0:
        #     break
        soup = BeautifulSoup(driver.page_source, "lxml")
        if soup.find("a", {"title": "Next"}):
            driver.find_element_by_xpath("//a[@title='Next']").click()
        else:
            break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
