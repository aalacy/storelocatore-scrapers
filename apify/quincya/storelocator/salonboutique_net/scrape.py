import csv
import re
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

log = SgLogSetup().get_logger("salonboutique.net")


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

    base_link = "http://www.salonboutique.net/directorymain/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).driver()

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    found = []

    sections = base.find(class_="post-content").find_all(class_="fusion-text")
    locator_domain = "salonboutique.net"

    for section in sections[2:]:
        main_link = section.a["href"]
        log.info(main_link)
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        next_items = base.find(class_="post-content").find_all(class_="fusion-text")
        for next_item in next_items:
            try:
                city_link = next_item.a["href"]
            except:
                continue
            log.info(city_link)
            req = session.get(city_link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                base.find(class_="lsd-load-more").text
                # selenium required to load more

                driver.get(city_link)

                WebDriverWait(driver, 50).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "lsd-load-more"))
                )
                time.sleep(1)
                driver.find_element_by_class_name("lsd-load-more").click()
                time.sleep(5)
                base = BeautifulSoup(driver.page_source, "lxml")
            except:
                pass

            items = base.find_all(class_="lsd-listing-body")

            for item in items:

                link = item.find(itemprop="url")["href"]
                if "salonboutique.net" not in link:
                    continue

                log.info(link)
                location_name = item.find(itemprop="url").text.strip()

                raw_address = (
                    item.find(itemprop="address")
                    .text.replace(", Ste", " Ste")
                    .replace(", ste", " ste")
                    .replace(", STE", " STE")
                    .replace("106 San", "106, San")
                    .replace("tonio TX", "tonio, TX")
                    .replace("tonio tx", "tonio, tx")
                    .replace("B Henderson", "B, Henderson")
                    .replace(", ,", ",")
                    .strip()
                    .split(",")
                )

                try:
                    street_address = (
                        raw_address[0].strip()
                        + " "
                        + item.find(class_="lsd-labels-list-item").text.strip()
                    )
                except:
                    street_address = raw_address[0].strip()

                if street_address in found:
                    continue
                found.append(street_address)
                city = raw_address[1].strip()
                state = raw_address[-1].strip().split()[0].strip().upper()
                if "Texas" in city:
                    city = city.replace("Texas", "")
                    state = "TX"
                try:
                    zip_code = raw_address[-1].strip().split()[1].strip()
                except:
                    zip_code = ""
                country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"

                try:
                    phone = (
                        item.find(itemprop="telephone")
                        .text.split("/")[0]
                        .split("Nicole")[0]
                        .split("- Amber")[0]
                        .split("Sara")[0]
                        .split("Monica")[0]
                        .split("Kathy")[0]
                        .split("Lindsey")[0]
                        .split("Karen")[0]
                        .split("Aubrey")[0]
                        .replace("Kelly Martin", "")
                        .replace("Aneta", "")
                        .replace("Jonas", "")
                        .strip()
                    )
                    if ".com" in phone:
                        phone = "<MISSING>"
                except:
                    phone = "<MISSING>"

                hours_of_operation = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"

                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")

                if not zip_code:
                    rows = base.find_all(class_="lsd-col-6")
                    for row in rows:
                        if "zip code" in str(row).lower():
                            zip_code = row.find(class_="lsd-attr-value").text

                try:
                    hours_of_operation = (
                        " ".join(
                            list(
                                base.find(
                                    class_="lsd-single-availability-box"
                                ).stripped_strings
                            )
                        )
                        .replace(" <br>Schedule at ToddKaneHair.com", "")
                        .replace("<br>", "")
                        .replace("<BR>", " ")
                        .replace("Text (713) 882-2933 for availability.", "")
                        .strip()
                    )
                except:
                    pass

                if (
                    hours_of_operation
                    == "Monday Tuesday Wednesday Thursday Friday Saturday Sunday"
                ):
                    hours_of_operation = "<MISSING>"

                try:
                    latitude = re.findall(r'latitude":[0-9]{2}\.[0-9]+', str(base))[
                        0
                    ].split(":")[1][:10]
                    longitude = re.findall(
                        r'longitude":-[0-9]{2,3}\.[0-9]+',
                        str(base),
                    )[0].split(":")[1][:12]
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"

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
