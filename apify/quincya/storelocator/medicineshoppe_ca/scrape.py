import csv
import re
import time

from random import randint

from bs4 import BeautifulSoup

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("medicineshoppe_ca")


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,\
    like Gecko) Chrome/72.0.3626.119 Safari/537.36"

    headers = {"User-Agent": user_agent}

    session = SgRequests()

    driver = SgChrome().chrome()

    data = []
    found = []
    locator_domain = "medicineshoppe.ca"

    ca_list = ["AB", "BC", "SK", "NS", "MB", "QC", "ON", "NT", "PE", "NL", "NU", "YT"]

    for i in ca_list:

        url = "https://www.medicineshoppe.ca/en/find-a-store?ad=%s" % i

        logger.info(i)
        driver.get(url)

        try:
            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.CLASS_NAME, "search-list"))
            )
        except TimeoutException:
            try:
                driver.get(url)
                WebDriverWait(driver, 100).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "search-list"))
                )
            except TimeoutException:
                continue

        time.sleep(randint(3, 5))

        base = BeautifulSoup(driver.page_source, "lxml")

        store_list = base.find(class_="search-list").find_all(class_="details")

        for st in store_list:
            link = "https://www.medicineshoppe.ca" + st["href"]
            if link in found:
                continue
            found.append(link)

            # logger.info(link)

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            location_name = base.h1.text.strip()
            try:
                store_number = location_name.split("#")[1].replace("(N)", "")
            except:
                store_number = "<MISSING>"

            try:
                location_type = ", ".join(
                    list(
                        base.find(
                            class_="pharmacy-general-services editable single"
                        ).ul.stripped_strings
                    )
                )
            except:
                location_type = "<MISSING>"

            address = base.address.text.strip().split(",")

            if len(address) == 4:
                street_address, city, state, zipcode = address
            state = state.replace("(", "").replace(")", "").strip()
            city = city.strip()
            street_address = street_address.strip()
            zipcode = zipcode.strip()

            try:
                phone = (
                    base.find(
                        "div",
                        attrs={
                            "class": "columns medium-12 large-6 pharmacy-content-infos"
                        },
                    )
                    .find("a")
                    .text
                )
            except:
                phone = "<MISSING>"
            hours_of_open = base.find(
                "div", attrs={"class": "table-hours-container"}
            ).find_all("tr")

            for t in range(len(hours_of_open)):
                hours_of_open[t] = " : ".join(
                    [h.text for h in hours_of_open[t].find_all("td")]
                )
            hours_of_open = " ".join(hours_of_open)

            try:
                map_str = str(base.find(class_="pharmacy-map-background"))
                latitude, longitude = re.findall(
                    r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str
                )[0].split(",")
            except:
                latitude = longitude = "<MISSING>"
            country_code = "CA"

            data.append(
                [
                    locator_domain,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zipcode,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_open,
                ]
            )

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
