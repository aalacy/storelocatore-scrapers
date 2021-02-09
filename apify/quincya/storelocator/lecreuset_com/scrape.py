import csv
import json
import re
import time

from random import randint

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sgselenium import SgChrome


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

    base_link = "https://www.lecreuset.com/stores"

    driver = SgChrome().chrome()
    time.sleep(2)

    driver.get(base_link)

    WebDriverWait(driver, 30).until(
        ec.presence_of_element_located((By.CLASS_NAME, "card-body"))
    )
    time.sleep(randint(3, 5))

    base = BeautifulSoup(driver.page_source, "lxml")

    data = []

    locator_domain = "lecreuset.com"

    stores = json.loads(base.find(class_="jumbotron")["data-locations"])

    for store in stores:
        location_name = store["name"]
        location_type = "<MISSING>"

        raw_data = BeautifulSoup(store["infoWindowHtml"], "lxml")

        street_address = raw_data.address.div.text.replace("\n", " ").strip()
        if "Caymans Islands" in street_address:
            continue
        city_line = raw_data.address.find_all("div")[1].text.replace("\n", "").strip()
        if not city_line:
            city_line = " ".join(street_address.split()[-3:]).split(",")
            street_address = " ".join(street_address.split()[:-3])
        elif "," in city_line:
            city_line = city_line.split(",")
        city = city_line[0]
        state = city_line[1].strip().split()[0].strip()
        try:
            zip_code = city_line[1].strip().split()[1].strip()
        except:
            zip_code = "<MISSING>"
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        if "null" in zip_code:
            zip_code = "<MISSING>"

        if "Suite" in city:
            street_address = street_address + " " + " ".join(city.split()[:2])
            city = " ".join(city.split()[2:])
        if "Suite 125 Miramar" in street_address:
            street_address = street_address.replace("Miramar", "").strip()
            city = "Miramar Beach"
        if "1911 Leesburg-Grove City" in street_address:
            street_address = street_address.replace("1098 Grove", "1098").strip()
            city = "Grove City"
        if "Canal St New" in street_address:
            street_address = street_address.replace("Canal St New", "Canal St").strip()
            city = "New York"

        street_address = (re.sub(" +", " ", street_address)).strip()

        country_code = "US"
        store_number = "<MISSING>"
        phone = raw_data.find(class_="storelocator-phone").text
        zip_code = zip_code.replace("01007", "10013")
        hours_of_operation = "<INACCESSIBLE>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = raw_data.find_all("a")[-1]["href"]

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

    try:
        driver.close()
    except:
        pass

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
