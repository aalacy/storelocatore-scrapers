import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('knowledgebeginnings_com')




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
    addresses = []
    driver = SgSelenium().firefox()
    driver.get("https://www.knowledgebeginnings.com/our-centers/locator/")
    states = []
    for button in driver.find_elements_by_xpath("//select[@name='ctl00$ContentPlaceHolder1$dropdownState']/option"):
        state = button.get_attribute("value")
        if len(state) != 2:
            continue
        states.append(state)
    # WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath(
    #     "//button[@id='onetrust-accept-btn-handler']")).click()
    # time.sleep(3)

    for state in states:

        # time.sleep(3)
        element = WebDriverWait(driver, 100).until(
            lambda x: x.find_element_by_xpath("//option[@value='" + state + "']"))
        create = driver.find_element_by_xpath(
            "//option[@value='" + state + "']")
        create.click()
        driver.find_element_by_xpath(
            "//input[@name='ctl00$ContentPlaceHolder1$buttonSubmit']").click()
        # exit()
        try:
            # logger.info("----------------------", state)
            element = WebDriverWait(driver, 10).until(
                lambda x: x.find_element_by_xpath("//li[@style='color:red; display:block']"))
            # logger.info("----------------------", state)
            continue
        except:
            pass
        element = WebDriverWait(driver, 20).until(
            lambda x: x.find_element_by_xpath("//li[@class='landing']"))
        soup = BeautifulSoup(driver.page_source, "lxml")
        try:
            for loc in soup.find("div", class_="clResultsPage").find_all("li"):
                list_loc = list(loc.stripped_strings)
                page_url = "https://www.knowledgebeginnings.com" + \
                    loc.find("a")["href"]
                location_name = list_loc[0].strip()
                street_address = list_loc[1].strip()
                city = list_loc[2].split(',')[0].strip()
                state = list_loc[2].split(',')[1].split()[0].strip()
                zipp = list_loc[2].split(',')[1].split()[-1].strip()
                phone = list_loc[3].strip()
                country_code = "US"
                location_type = "<MISSING>"
                store_number = page_url.split('/')[-2].strip()
                hours_of_operation = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                store = []
                store.append("https://www.knowledgebeginnings.com")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append(store_number)
                store.append(phone)
                store.append(location_type)  # location type
                store.append(latitude)  # lat
                store.append(longitude)  # lng
                store.append(hours_of_operation)  # hours
                store.append(page_url)  # page_url
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                # logger.info(store)
                # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                yield store

        except:
            pass
            # logger.info(state)

        driver.find_element_by_xpath("//li[@class='landing']").click()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
