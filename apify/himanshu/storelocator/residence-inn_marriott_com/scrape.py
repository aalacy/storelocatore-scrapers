import csv
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
import unicodedata


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)




def initial_search(driver, brand_id):
    # driver.get("https://www.marriott.com/search/submitSearch.mi?showMore=true&marriottBrands=" +
    #    str(brand_id) + "&destinationAddress.country=US")
    driver.get("https://www.marriott.com/search/default.mi")
    element = WebDriverWait(driver, 30).until(
        lambda x: x.find_element_by_xpath('//input[@id="keywords"]'))
    element.send_keys("residenceinn")
    WebDriverWait(driver, 30).until(lambda x: x.find_element_by_xpath(
        '//input[@value="Search Hotels"]')).click()


def fetch_data():

    addresses = []
    brand_id = "RI"
    domain_url = "https://residence-inn.marriott.com"

    driver = SgSelenium().firefox()
    initial_search(driver, brand_id)
    # attempt to handle server error on initial search
    if "Our server is being stubborn, please try again" in driver.page_source:
        initial_search(driver, brand_id)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.js-property-list-container')))

    while True:

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
            if state in ["QROO", "JAL", "DF", "NL", "YUC"]:
                continue
            store_zip = address["data-postal-code"]
            phone = address["data-contact"]
            if "+1" not in phone:
                continue
            lat = json.loads(location["data-property"])["lat"]
            lng = json.loads(location["data-property"])["longitude"]
            page_url = "https://www.marriott.com" + \
                location.find(
                    "span", {"class": "l-property-name"}).parent.parent["href"]
            store = []
            store.append(domain_url)
            store.append(name if name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            if store[-1] == "":
                continue
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            ca_zip_list = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(store_zip))
            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(store_zip))
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            elif us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            else:
                continue
            store.append(zipp if zipp else "<MISSING>")
            if len(store[-1]) == 10:
                store[-1] = store[-1].replace(" ", "-")
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("Residence Inn")
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
            yield store
            # print("data === ",store)
            # print("data === ",str(store))
        # if len(soup.find('div',{'class':'js-property-list-container'}).find_all("div",{"data-brand":str(brand_id)})) <= 0:
        #     break

        time.sleep(2)
        try:
            WebDriverWait(driver, 20).until(
                lambda x: x.find_element_by_xpath("//a[@title='Next']")).click()
        except (NoSuchElementException, TimeoutException, WebDriverException):
            break

    driver.close()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
