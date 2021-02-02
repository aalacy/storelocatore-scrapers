import csv
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgselenium import SgChrome

log = SgLogSetup().get_logger("peets.com")


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

    driver = SgChrome().chrome()

    data = []
    all_links = []

    locator_domain = "peets.com"

    base_link = "https://locations.peets.com/site-map/all"

    driver.get(base_link)
    WebDriverWait(driver, 50).until(
        ec.presence_of_element_located(
            (By.CSS_SELECTOR, ".sitemap-location.ng-binding")
        )
    )
    time.sleep(1)

    base = BeautifulSoup(driver.page_source, "lxml")
    items = base.find_all(class_="sitemap-location ng-binding")

    for item in items:
        link = "https://locations.peets.com" + item["href"]
        all_links.append(link)

    log.info("Processing " + str(len(all_links)) + " links..can take up to 1 hour ..")
    for link in all_links:
        driver.get(link)
        WebDriverWait(driver, 50).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".no-margin.ng-binding"))
        )
        time.sleep(1)

        item = BeautifulSoup(driver.page_source, "lxml")

        location_name = item.h1.text.strip()
        street_address = (
            item.find_all("span", attrs={"itemprop": "streetAddress"})[-1]
            .get_text(" ")
            .strip()
        )
        city = item.find("span", attrs={"itemprop": "addressLocality"}).text.strip()
        state = item.find("span", attrs={"itemprop": "addressRegion"}).text.strip()
        zip_code = item.find("span", attrs={"itemprop": "postalCode"}).text.strip()
        if len(zip_code) < 5:
            zip_code = "0" + zip_code
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        country_code = "US"
        phone = item.find("div", attrs={"itemprop": "telephone"}).text.strip()
        try:
            if (
                "temporarily closed"
                in item.find(class_="closed-store ng-binding").text.lower()
            ):
                hours_of_operation = "Temporarily Closed"
        except:
            hours_of_operation = item.find("dl", attrs={"itemprop": "openingHours"})[
                "content"
            ].strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            else:
                if "Sa" not in hours_of_operation:
                    hours_of_operation = hours_of_operation + " Sa Closed"
                if "Su" not in hours_of_operation:
                    hours_of_operation = hours_of_operation + " Su Closed"
        latitude = item.find("meta", attrs={"itemprop": "latitude"})["content"]
        longitude = item.find("meta", attrs={"itemprop": "longitude"})["content"]

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
