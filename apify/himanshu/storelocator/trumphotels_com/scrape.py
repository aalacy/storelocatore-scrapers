# -*- coding: utf-8 -*-

import csv
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sgselenium import SgChrome
from selenium import webdriver


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def get_driver():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"

    chrome = SgChrome()
    options = webdriver.ChromeOptions()
    chrome._SgSelenium__add_chrome_arguments(options, user_agent)

    driver = webdriver.Chrome(options=options)
    chrome._SgSelenium__configure_chromedriver(driver, user_agent)
    return driver


def fetch_data():
    driver = get_driver()
    base_url = "https://www.trumphotels.com"
    driver.get(base_url)
    soup = BeautifulSoup(driver.page_source, "lxml")

    for country in soup.find("div", class_="ourhotels-list-container").find_all(
        "div", {"class": "filterlist"}
    ):
        for location in country.find_all("a"):
            page_url = urljoin(base_url, location["href"])
            driver.get(page_url)
            location_soup = BeautifulSoup(driver.page_source, "html5lib")

            for script in location_soup.find_all(
                "script", {"type": "application/ld+json"}
            ):
                if "address" in json.loads(script.text):
                    store_data = json.loads(script.text)
                    if store_data["address"]["addressCountry"] not in ("USA", "Canada"):
                        continue

                    name = location.text.strip()
                    address = store_data["address"]
                    geo_location = location_soup.find("div", {"class": "map-outer-div"})

                    store = []
                    store.append("https://www.trumphotels.com")
                    store.append(name.replace("®", ""))
                    store.append(address["streetAddress"])
                    store.append(address["addressLocality"].split(",")[0])
                    store.append(
                        address["addressRegion"]
                        if "addressRegion" in address
                        else address["addressLocality"].split(",")[1]
                    )
                    store.append(address["postalCode"])
                    store.append("US" if address["addressCountry"] == "USA" else "CA")
                    store.append("<MISSING>")
                    store.append(
                        store_data["telephone"]
                        if store_data["telephone"]
                        else "<MISSING>"
                    )
                    store.append(store_data["@type"])
                    store.append(geo_location["data-latitude"])
                    store.append(geo_location["data-longitude"])
                    store.append("<MISSING>")
                    store.append(page_url)
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
