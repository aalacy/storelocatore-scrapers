import csv
import json
import re
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("theroomplace_com")


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


def addy_ext(addy):
    address = addy.split(" ")
    if len(address) == 4:
        city = address[0] + " " + address[1]
        state = address[2]
        zip_code = address[3]
    else:
        city = address[0]
        state = address[1]
        zip_code = address[2]
    return city.replace(",", ""), state, zip_code


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    locator_domain = "https://www.theroomplace.com/"
    ext = "location-view-all"

    driver = SgChrome(user_agent=user_agent).driver()
    driver1 = SgChrome(user_agent=user_agent).driver()
    driver.get(locator_domain + ext)
    time.sleep(8)

    try:
        element = driver.find_element_by_css_selector("a.ltkmodal-close")
        driver.execute_script("arguments[0].click();", element)
    except:
        pass

    divs = driver.find_elements_by_css_selector("div.dl-storelocator-info")

    all_store_data = []
    for div in divs:
        link = (
            "https://www.theroomplace.com/location/"
            + div.find_element_by_css_selector(
                ".mz-locationlisting-name.show-store-detail"
            ).get_attribute("data-store-slug")
        )
        logger.info(link)
        content = div.text.split("\n")
        location_name = content[0]
        street_address = content[1].replace("(Route 30)", "").strip()
        if "main showroom" in street_address.lower():
            street_address = content[-3]
        city, state, zip_code = addy_ext(content[-2])
        location_type = "<MISSING>"
        phone_number = content[-1]
        country_code = "US"
        raw_hours = (
            div.find_element_by_css_selector(".dl-store-hours-container.hidden")
            .get_attribute("innerText")
            .strip()
        )
        hours = raw_hours[5 : raw_hours.find("Schedule")].replace("\n", "")
        hours = (re.sub(" +", " ", hours)).strip()
        store_number = div.find_element_by_css_selector(
            ".mz-locationlisting-name.show-store-detail"
        ).get_attribute("data-store-id")

        driver1.get(link)
        time.sleep(2)
        WebDriverWait(driver1, 50).until(
            ec.presence_of_element_located((By.CLASS_NAME, "location-item"))
        )
        time.sleep(20)
        base = BeautifulSoup(driver1.page_source, "lxml")

        fin_script = ""
        all_scripts = base.find_all("script", attrs={"type": "application/ld+json"})
        for script in all_scripts:
            if "latitude" in str(script):
                fin_script = script.contents[0]
                break
        if fin_script:
            try:
                store = json.loads(fin_script)
                lat = store["geo"]["latitude"]
                longit = store["geo"]["longitude"]
            except:
                lat = "<MISSING>"
                longit = "<MISSING>"
        else:
            lat = "<INACCESSIBLE>"
            longit = "<INACCESSIBLE>"

        store_data = [
            locator_domain,
            link,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
        ]
        all_store_data.append(store_data)

    driver.quit()
    driver1.quit()
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
