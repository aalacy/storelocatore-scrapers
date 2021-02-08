# -*- coding: utf-8 -*-
import csv
import json
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

log = SgLogSetup().get_logger("claimjumper.com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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


def fetch_data():

    driver = SgChrome().chrome()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "http://claimjumper.com/"
    r = session.get("https://www.claimjumper.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for loc in soup.find_all("p", class_="locationsList"):
        add = list(loc.stripped_strings)

        temp_closed = False
        if "temporarily close" in add[1].lower():
            temp_closed = True
        if "," not in add[2]:
            add.pop(1)
        street_address = add[1].strip()
        city = add[2].split(",")[0].strip().replace("Tualatin", "Portland")
        location_name = add[0].strip()
        state = add[2].split(",")[1].split()[0].strip()
        zipp = add[2].split(",")[1].split()[-1].strip()
        country_code = "US"
        phone = add[-1].strip()
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        page_url = (
            "https://www.claimjumper.com"
            + loc.find("a", class_="locationLink")["href"].strip()
        )

        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        longitude = ""
        latitude = ""
        hours_of_operation = ""

        log.info(page_url)
        driver.get(page_url)

        try:
            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.ID, "mfLocationJsonLD"))
            )
        except:
            pass

        time.sleep(8)

        soup2 = BeautifulSoup(driver.page_source, "lxml")

        if temp_closed:
            hours_of_operation = "Temporarily Closed"
        else:
            try:
                hours_of_operation = (
                    " ".join(
                        list(
                            soup2.find(
                                class_="mat-list mat-list-base mf-hours-list"
                            ).stripped_strings
                        )
                    )
                    .replace("Hours", "")
                    .strip()
                )
            except:
                try:
                    hours_of_operation = (
                        " ".join(
                            list(
                                soup1.find(
                                    "h5", class_="hoursHeader"
                                ).parent.stripped_strings
                            )
                        )
                        .replace("hours", "")
                        .strip()
                    )
                except:
                    hours_of_operation = "<MISSING>"
        try:
            js = json.loads(soup2.find(id="mfLocationJsonLD").text)
            latitude = js["geo"]["latitude"]
            longitude = js["geo"]["longitude"]
        except:
            try:
                latitude = soup1.find("span", {"id": "jsLat"}).text.strip()
                longitude = soup1.find("span", {"id": "jsLong"}).text.strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

        store = [
            locator_domain,
            location_name,
            street_address.replace("Opry Mills Mall, ", ""),
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            page_url,
        ]

        store = [str(x).replace("–", "-").strip() if x else "<MISSING>" for x in store]
        yield store
    driver.close()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
