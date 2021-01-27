import csv
import re
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

from sglogging import SgLogSetup

from sgselenium import SgChrome

import usaddress

logger = SgLogSetup().get_logger("odfl_com")


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


def parse_address(address):
    address = usaddress.parse(address)
    street = ""
    city = ""
    for addr in address:
        if addr[1] == "PlaceName":
            city += addr[0].replace(",", "") + " "
        else:
            street += addr[0].replace(",", "") + " "
    if not city:
        city = street.split()[-1]
        street = " ".join(street.split()[:-1])
    return street.strip(), city.strip()


def fetch_data():
    addresses = []
    driver = SgChrome().chrome()
    driver.get("https://www.odfl.com/ServiceCenterLocator/locator.faces")
    time.sleep(3)
    driver.find_element_by_tag_name("body").send_keys(Keys.ESCAPE)
    time.sleep(5)
    try:
        driver.find_element_by_id("onetrust-accept-btn-handler").click()
    except:
        pass
    states = []
    for button in driver.find_elements_by_xpath(
        "//select[@name='locatorForm:j_idt40']/option"
    ):
        state = button.get_attribute("value")
        if len(state) != 2:
            continue
        states.append(state)
    time.sleep(3)

    for state in states:
        logger.info(state)
        WebDriverWait(driver, 100).until(
            lambda x: x.find_element_by_xpath("//option[@value='" + state + "']")
        )
        create = driver.find_element_by_xpath("//option[@value='" + state + "']")
        create.click()
        driver.find_element_by_xpath("//input[@name='locatorForm:j_idt44']").click()
        try:
            WebDriverWait(driver, 5).until(
                lambda x: x.find_element_by_xpath(
                    "//li[@style='color:red; display:block']"
                )
            )
            continue
        except:
            pass
        WebDriverWait(driver, 30).until(
            lambda x: x.find_element_by_xpath("//input[@value='Return']")
        )
        soup = BeautifulSoup(driver.page_source, "lxml")
        for location in soup.find("table", {"border": "4"}).find_all("td"):
            name = location.find("h4").text.strip()
            address = list(location.stripped_strings)[1]
            phone = list(location.stripped_strings)[2]
            zip_split = re.findall(
                r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}", address
            )
            country = ""
            if zip_split:
                store_zip = zip_split[-1]
                if len(store_zip) == 6:
                    store_zip = store_zip[:3] + " " + store_zip[3:]
                country = "CA"
            else:
                zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b", address)
                store_zip = zip_split[-1]
                country = "US"
            state_split = re.findall("([A-Z]{2})", address)
            if state_split:
                state = state_split[-1]
            else:
                state = "<MISSING>"

            if country == "US":
                raw_address = (
                    address.replace(" " + state + " ", "")
                    .replace(store_zip, "")
                    .replace(",", "")
                    .strip()
                )
                street, city = parse_address(raw_address)
            else:
                raw_address = address[: address.rfind(state)].strip()
                city = raw_address.split()[-1].strip()
                street = raw_address[: raw_address.rfind(city)].strip()
                city = (
                    city.replace("GEORGE", "PRINCE GEORGE")
                    .replace("COQUITLAM", "PORT COQUITLAM")
                    .replace(",", "")
                    .strip()
                )
                street = street.split("PRINCE")[0].split("PORT")[0].strip()

            if (
                "ACRE DRIVE GRAND" in street
                or "1780 W 2550 N" in street
                or "16811 ENTERPRISE BLVD" in street
                or "WRIGHT AVENUE TWIN" in street
                or "WEST OAKTON DES" in street
                or "ELDER RD WEST BOX" in street
                or "HWY 212 SACRED" in street
                or "US 41 FORT" in street
                or "FLAGSTONE ROAD FORT" in street
            ):
                city = street[street.rfind(" ") + 1 :].strip() + " " + city
                street = street[: street.rfind(" ")].strip()

            if "BLVD" in city:
                city = city.replace("BLVD", "").strip()
                street = street + " BLVD"

            store = []
            store.append("https://www.odfl.com")
            store.append(name)
            store.append(street)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append(country)
            store.append("<MISSING>")
            store.append(phone.split(":")[1] if "Phone" in phone else "<MISSING>")
            store.append("<MISSING>")  # location type
            store.append("<MISSING>")  # lat
            store.append("<MISSING>")  # lng
            store.append("<MISSING>")  # hours
            store.append("<MISSING>")  # page_url
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
        driver.find_element_by_xpath("//input[@value='Return']").click()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
