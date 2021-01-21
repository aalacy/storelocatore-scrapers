import csv
import json
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgselenium import SgChrome

log = SgLogSetup().get_logger("onemainfinancial.com")


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


def get_base(driver):
    base = BeautifulSoup(driver.page_source, "lxml")
    if not base.text:
        time.sleep(2)
        base = BeautifulSoup(driver.page_source, "lxml")
    return base


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).chrome()

    data = []
    final_links = []

    locator_domain = "https://www.onemainfinancial.com"

    base_link = "https://www.onemainfinancial.com/branches"
    driver.get(base_link)

    WebDriverWait(driver, 50).until(
        ec.presence_of_element_located((By.CLASS_NAME, "state-branches"))
    )
    base = get_base(driver)

    # Getting final page links
    state_links = base.find(class_="state-branches").find_all("a")
    for link in state_links:
        state_link = locator_domain + link["href"]
        log.info(state_link)
        driver.get(state_link)

        WebDriverWait(driver, 50).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, ".bulletless.inline.city-branches.spaced-2x")
            )
        )
        base = get_base(driver)

        city_links = base.find(
            class_="bulletless inline city-branches spaced-2x"
        ).find_all("a")
        for link in city_links:
            city_link = locator_domain + link["href"]
            if city_link.split("/")[-1].isdigit():
                final_links.append(city_link)
            else:
                driver.get(city_link)

                WebDriverWait(driver, 50).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "fn"))
                )
                base = get_base(driver)

                more_links = base.find_all(class_="fn")
                for link in more_links:
                    final_links.append(locator_domain + link.a["href"])

    # Scraping final pages
    log.info("Processing %s final_links .." % len(final_links))
    for final_link in final_links:
        driver.get(final_link)
        time.sleep(1)
        WebDriverWait(driver, 50).until(
            ec.presence_of_element_located((By.ID, "maincontent"))
        )

        try:
            script = (
                driver.find_element_by_id("maincontent")
                .find_elements_by_tag_name("script")[1]
                .get_attribute("innerText")
            )
        except:
            time.sleep(1)
            script = (
                driver.find_element_by_id("maincontent")
                .find_elements_by_tag_name("script")[1]
                .get_attribute("innerText")
            )

        if "virtual" in driver.find_element_by_tag_name("h1").text.lower():
            continue

        store = json.loads(script)

        location_name = store["name"]
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        country_code = "US"
        store_number = final_link.split("/")[-1]
        location_type = "<MISSING>"
        phone = store["telephone"]
        hours_of_operation = " ".join(store["openingHours"])
        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

        # Store data
        data.append(
            [
                locator_domain,
                final_link,
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
