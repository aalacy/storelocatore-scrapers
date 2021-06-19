import csv
import re
import ssl
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("members1st_org")

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


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

    base_link = "https://www.members1st.org/atm-and-locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).driver()

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="row justify-content-between").find_all("li")
    locator_domain = "members1st.org"

    for item in items:
        link = "https://www.members1st.org" + item.a["href"]
        logger.info(link)
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()
        street_address = base.find(
            "span", attrs={"itemprop": "streetAddress"}
        ).text.strip()
        city = (
            base.find("span", attrs={"itemprop": "addressLocality"})
            .text.split(",")[0]
            .strip()
        )
        state = (
            base.find("span", attrs={"itemprop": "addressLocality"})
            .text.split(",")[1]
            .strip()
        )
        zip_code = base.find("span", attrs={"itemprop": "postalCode"}).text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = (
            base.find(class_="services-table").text.strip().replace("\n", ",")
        )
        phone = (
            base.find("span", attrs={"itemprop": "telephone"})
            .text.replace("Phone:", "")
            .strip()
        )
        hours_of_operation = (
            base.find(class_="lobby-hours")
            .text.replace("Lobby Hours", "")
            .strip()
            .replace("\n", " ")
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        map_link = base.find(class_="b_map_img")["src"]
        driver.get(map_link)
        time.sleep(4)
        try:
            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.TAG_NAME, "a"))
            )
            time.sleep(4)
            raw_gps = driver.find_element_by_tag_name("a").get_attribute("href")
            latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find(",")].strip()
            longitude = raw_gps[raw_gps.find(",") + 1 : raw_gps.find("&")].strip()
        except:
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"

        yield [
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
    driver.close()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
