import csv
import json
import time

from bs4 import BeautifulSoup

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgselenium import SgChrome

log = SgLogSetup().get_logger("pacsun.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_link = "https://www.pacsun.com/stores"

    driver = SgChrome().chrome()
    time.sleep(2)

    data = []

    for i in range(1, 60):

        driver.get(base_link)
        WebDriverWait(driver, 30).until(
            ec.presence_of_element_located((By.ID, "dwfrm_storelocator_state"))
        )
        time.sleep(2)

        state_list = Select(driver.find_element_by_name("dwfrm_storelocator_state"))
        try:
            state_list.select_by_index(i)
        except NoSuchElementException:
            break

        log.info(state_list.options[i].text)
        time.sleep(1)
        search = driver.find_element_by_name("dwfrm_storelocator_findbystate")
        driver.execute_script("arguments[0].click();", search)

        time.sleep(1)
        base = BeautifulSoup(driver.page_source, "lxml")
        stores = base.find_all(class_="sl-store")

        if not stores:
            continue

        locator_domain = "pacsun.com"

        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "storeList" in str(script):
                script = str(script)
                break
        js = script.split("=")[1].split("}]")[0] + "}]"
        store_json = json.loads(js)

        for store in stores:
            location_name = store.h2.text.strip()
            if "CLOSED" in location_name.upper():
                continue

            link = "<MISSING>"

            phone = store.find(class_="phone-number").text.strip()

            street_address = store.find(class_="address-phone-info").div.text.strip()
            city_line = (
                store.find(class_="address-phone-info")
                .find_all("div")[1]
                .text.strip()
                .replace("\t", "")
                .split("\n")
            )
            city = city_line[0].replace(",", "")
            state = city_line[1]
            zip_code = city_line[2]
            country_code = "US"
            store_number = store["id"]
            location_type = "<MISSING>"

            hours_of_operation = store.find(class_="storehours").get_text(" ").strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            for j in store_json:
                if j["ID"] == store_number:
                    latitude = j["lat"]
                    longitude = j["long"]
                    break

            data.append(
                [
                    locator_domain,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
