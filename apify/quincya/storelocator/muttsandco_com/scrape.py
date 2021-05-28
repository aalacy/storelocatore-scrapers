import csv
import re
import time

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("muttsandco_com")


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

    base_link = "https://muttsandco.com/pages/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    driver = SgChrome(user_agent=user_agent).driver()

    data = []

    items = base.find(id="desktop-menu-0-7").find_all("a")
    locator_domain = "muttsandco.com"

    for item in items:
        link = "https://muttsandco.com" + item["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = "Mutts & Co - " + base.h1.text.strip()
        logger.info(link)

        raw_address = base.find(
            style="font-size: 16px; font-family: Poppins;"
        ).text.split(",")
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].strip().split()[0].strip()
        zip_code = raw_address[2].strip().split()[1].strip()

        country_code = "US"
        store_number = "<MISSING>"

        location_type = (
            base.find_all(style="font-size: 16px; font-family: Poppins;")[1]
            .text.replace("Services", "")
            .strip()
            .replace("\n\n\n", ",")
            .replace("\n", "")
            .replace(" •", ",")
        )
        location_type = (re.sub(" +", " ", location_type)).strip()
        try:
            phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", str(base))[0]
        except:
            phone = "<MISSING>"

        if location_type == phone:
            location_type = (
                base.find_all(style="font-size: 16px; font-family: Poppins;")[2]
                .text.replace("Services", "")
                .strip()
                .replace("\n\n\n", ",")
                .replace("\n", "")
                .replace(" •", ",")
            )
            location_type = (re.sub(" +", " ", location_type)).strip()

        hours_of_operation = (
            base.find_all(class_="shg-rich-text shg-theme-text-content")[-1]
            .ul.text.replace("\n", " ")
            .strip()
        )

        try:
            driver.get(link)
            time.sleep(10)
            raw_gps = driver.find_element_by_xpath(
                "//*[(@title='Open this area in Google Maps (opens a new window)')]"
            ).get_attribute("href")
            latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find(",")].strip()
            longitude = raw_gps[raw_gps.find(",") + 1 : raw_gps.find("&")].strip()
        except:
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"

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
