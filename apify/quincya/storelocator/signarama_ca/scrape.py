import csv
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("signarama_ca")


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

    base_link = "https://signarama.ca/location/locator.php"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()

    logger.info("Loading page items ..")
    driver.get(base_link)

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "nearyou")))
    time.sleep(2)

    load_btn = driver.find_element_by_xpath("//a[(@onclick='moreResults()')]")

    prev_amt = 0
    for i in range(10):
        driver.execute_script("arguments[0].click();", load_btn)
        time.sleep(5)
        base = BeautifulSoup(driver.page_source, "lxml")
        items = base.find(id="nearyou").find_all("div", recursive=False)

        if len(items) == prev_amt:
            break

        prev_amt = len(items)

    data = []

    locator_domain = "signarama.ca"

    logger.info("%s locations found!" % (len(items)))
    for item in items:
        link = "https://signarama.ca" + item.a["href"]
        location_name = item["data-name"]
        try:
            street_address = list(item.find_all(class_="m-0")[1].stripped_strings)[0]
        except:
            street_address = list(item.find_all(class_="m-0")[0].stripped_strings)[0]
        street_address = street_address.replace("  ", " ")
        city = item["data-city"]
        state = item["data-state"]
        zip_code = item["data-zip"]
        country_code = "CA"
        store_number = "<MISSING>"
        phone = item["data-phone"]
        latitude = item["data-latitude"]
        longitude = item["data-longitude"]
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
