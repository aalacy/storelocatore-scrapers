import csv
import time

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

    base_link = "https://manchuwok.com/locations/"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    driver = SgChrome(user_agent=user_agent).chrome()
    time.sleep(2)

    driver.get(base_link)

    WebDriverWait(driver, 30).until(
        ec.presence_of_element_located((By.ID, "storeLocator__storeList"))
    )
    time.sleep(10)

    base = BeautifulSoup(driver.page_source, "lxml")
    items = base.find(id="storeLocator__storeList").find_all(
        class_="store-locator__infobox"
    )

    data = []
    found_poi = []

    locator_domain = "manchuwok.com"
    for item in items:
        location_name = item.find(
            class_="infobox__row infobox__title store-location"
        ).text.strip()
        if "closed" in location_name.lower():
            continue

        raw_address = (
            item.find(class_="infobox__row store-address").text.strip().split("  ")
        )

        street_address = raw_address[0].strip()
        if street_address in found_poi:
            continue
        found_poi.append(street_address)

        city = raw_address[1].replace(",", "").strip()
        state = raw_address[2].split()[0].strip()
        if len(state) > 3:
            continue
        zip_code = raw_address[2].strip()[3:].strip()
        if len(zip_code) > 7:
            continue
        if not zip_code:
            zip_code = "<MISSING>"
        if len(zip_code) < 5:
            continue

        if " " in zip_code:
            country_code = "CA"
        else:
            country_code = "US"

        store_number = item["id"]
        location_type = "<MISSING>"
        phone = "<MISSING>"

        latitude = (
            item.find(class_="infobox__row infobox__cta ssflinks")["href"]
            .split("(")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            item.find(class_="infobox__row infobox__cta ssflinks")["href"]
            .split("(")[1]
            .split(",")[1][:-1]
            .strip()
        )

        try:
            hours_of_operation = (
                item.find(class_="infobox__row store-operating-hours")
                .get_text(" ")
                .strip()
            )
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
        except:
            hours_of_operation = "<MISSING>"

        data.append(
            [
                locator_domain,
                base_link,
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
    return data

    try:
        driver.close()
    except:
        pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
