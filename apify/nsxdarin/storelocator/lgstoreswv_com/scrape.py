import csv
import re
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgselenium import SgChrome

log = SgLogSetup().get_logger("lgstoreswv.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    driver = SgChrome().chrome(user_agent=user_agent)

    url = "https://lgstoreswv.com/locations/"
    driver.get(url)
    WebDriverWait(driver, 50).until(
        ec.presence_of_element_located((By.CLASS_NAME, "owl-item"))
    )
    time.sleep(2)
    base = BeautifulSoup(driver.page_source, "lxml")

    if "Access from your Country was disabled" in str(base):
        log.info("Geo Blocked!")
    else:
        log.info("Page loaded!")

    data = []
    found = []
    website = "lgstoreswv.com"
    country = "US"
    hours = "<MISSING>"

    items = base.find_all(class_="owl-item")
    for item in items:
        if "data-address" in str(item):
            name = item.find(class_="wpgmza_carousel_info_holder").find_all("p")[1].text
            if name in found:
                continue
            found.append(name)
            store = name.split("#")[1].strip()
            addinfo = (
                item.find(class_="wpgmza_carousel_info_holder")
                .find_all("p")[2]
                .text.replace("Avenue, SW", "Avenue SW")
                .replace("Rd - Hunting", "Rd, Hunting")
            )
            add = addinfo.split(",")[0]
            city = addinfo.split(",")[1].strip()
            state = addinfo.split(",")[-1][:-5].strip()
            zc = addinfo.rsplit(" ", 1)[1]
            phone = (
                item.find(class_="wpgmza_carousel_info_holder")
                .find_all("p")[-3]
                .text.strip()
            )
            if "," in phone:
                try:
                    phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", str(item))[0]
                except:
                    phone = "<MISSING>"
            if "-" not in phone:
                phone = "<MISSING>"
            typ = item.img["src"].split("/")[-1].split("-MapIcon")[0].strip()
            lat = item.div["data-latlng"].split(",")[0].strip()
            lng = item.div["data-latlng"].split(",")[1].strip()
            purl = "https://lgstoreswv.com/locations/"

            data.append(
                [
                    website,
                    purl,
                    name,
                    add,
                    city,
                    state,
                    zc,
                    country,
                    store,
                    phone,
                    typ,
                    lat,
                    lng,
                    hours,
                ]
            )
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
