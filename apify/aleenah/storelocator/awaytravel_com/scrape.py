import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgselenium import SgChrome
import time
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("awaytravel_com")

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


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


session = SgRequests()


def fetch_data():
    # Your scraper here
    with SgChrome() as driver:
        res = session.get("https://www.awaytravel.com/ca/en/")
        soup = BeautifulSoup(res.text, "html.parser")
        stores = re.findall(r'href="(/ca/en/stores/[^"]+)"', str(soup))
        all = []
        for store in stores:
            url = "https://www.awaytravel.com" + store
            logger.info(url)
            if "london" in url:
                con = "UK"
            else:
                con = "US"
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            ll = soup.find("div", {"class": "store__map js-map"}).get("data-map")
            loc = soup.find("h1", {"class": "heading--1"}).text
            lat = re.findall(r'"lat": (-?[\d\.]*)', ll)[0]
            long = re.findall(r'"lng": (-?[\d\.]*)', ll)[0]
            street = soup.find("span", {"itemprop": "streetAddress"}).text
            city = soup.find("span", {"itemprop": "addressLocality"}).text
            state = soup.find("span", {"itemprop": "addressRegion"}).text
            zip = soup.find("span", {"itemprop": "postalCode"}).text
            if re.findall(r"[A-Z][0-9][A-Z] [0-9][A-Z][0-9]", zip) != []:
                con = "CA"

            tim = (
                soup.find_all("div", {"class": "store__address__details"})[1]
                .text.strip()
                .replace("\n", ", ")
            )

            if tim == "":
                tim = "<MISSING>"
            try:
                phone = soup.find("a", {"itemprop": "telephone"}).text.strip()
            except:
                phone = "<MISSING>"

            all.append(
                [
                    "https://www.awaytravel.com",
                    loc,
                    street,
                    city.replace(",", ""),
                    state,
                    zip,
                    con,
                    "<MISSING>",  # store #
                    phone,  # phone
                    "<MISSING>",  # type
                    lat,  # lat
                    long,  # long
                    tim.strip().replace("   ", " "),  # timing
                    url,
                ]
            )

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
