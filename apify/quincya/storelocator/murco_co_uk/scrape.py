import csv
import json
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sgrequests import SgRequests

from sgselenium import SgChrome


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    base_link = "https://murco.co.uk/station-finder/"

    driver = SgChrome().chrome()

    driver.get(base_link)
    time.sleep(2)
    WebDriverWait(driver, 50).until(
        ec.presence_of_element_located((By.ID, "map-canvas"))
    )
    time.sleep(4)
    base = BeautifulSoup(driver.page_source, "lxml")

    data = []

    locator_domain = "murco.co.uk"

    fin_script = ""
    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "address_1" in str(script):
            fin_script = script.text.replace("\n", "").strip()
            break

    js = fin_script.split("var stations =")[1].split("}};")[0] + "}}"
    stores = json.loads(js)

    for i in stores:
        store = stores[i]
        location_name = store["name"].replace("#038;", "").replace("&#8217;", "'")
        street_address = store["address_1"]
        zip_code = store["postcode"]
        country_code = "UK"
        store_number = i
        location_type = "<MISSING>"
        phone = store["telephone"]
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lon"]
        link = store["link"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(
            base.find(class_="col-lg-3 col-md-3 col-sm-3").p.stripped_strings
        )
        city = raw_address[-3]
        state = raw_address[-2]

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
