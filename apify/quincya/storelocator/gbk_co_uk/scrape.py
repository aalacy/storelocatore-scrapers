import csv
import json
import re
import time

from bs4 import BeautifulSoup

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("gbk_co_uk")


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

    base_link = "https://gbk.co.uk/find-your-gbk"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}
    options = Options()

    driver = SgChrome(
        user_agent=user_agent,
        chrome_options=options.add_argument("--ignore-certificate-errors"),
    ).driver()
    driver.get(base_link)
    WebDriverWait(driver, 50).until(
        ec.presence_of_element_located((By.CLASS_NAME, "restaurant_card"))
    )
    time.sleep(2)
    base = BeautifulSoup(driver.page_source, "lxml")

    session = SgRequests()

    data = []

    locator_domain = "https://gbk.co.uk"

    stores = base.find_all(class_="restaurant_card")

    for store in stores:
        link = locator_domain + store.find(class_="restaurant_link")["href"]
        logger.info(link)

        location_name = store.h3.text
        raw_address = store.address.text.split(",")
        street_address = " ".join(raw_address[:-2]).strip()
        street_address = (re.sub(" +", " ", street_address)).strip()
        city = city = raw_address[-2].strip()
        state = "<MISSING>"
        zip_code = raw_address[-1].strip()
        country_code = "GB"
        location_type = "<MISSING>"

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        js = (
            str(base)
            .replace("&quot;", '"')
            .replace('restaurant-data="', "restaurant-data='")
            .replace('"><', "'><")
            .split("restaurant-data='")[1]
            .split("'><")[0]
        )
        store_data = json.loads(js)

        store_number = store_data["restaurant_id"]
        if not store_number:
            store_number = "<MISSING>"
        phone = store_data["telephone_display"]
        if not phone:
            phone = "<MISSING>"
        latitude = store_data["latitude"]
        longitude = store_data["longitude"]

        hours_of_operation = ""
        raw_hours = store_data["opening_hours"]
        for hours in raw_hours:
            day = hours["day"]
            if hours["restaurant_closed"]:
                times = "Closed"
            else:
                opens = hours["opening_time"]
                closes = hours["closing_time"]
                times = opens + "-" + closes
            if opens != "" and closes != "":
                clean_hours = day + " " + times
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

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
