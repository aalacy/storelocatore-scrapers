import csv
import re
import ssl
import time

from random import randint

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgselenium import SgChrome

logger = SgLogSetup().get_logger("esportafitness_com")

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

    base_link = "https://www.esportafitness.com/Pages/FindClub.aspx"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).driver()

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    states = base.find(id="ctl00_MainContent_FindAClub1_cboSelState").find_all(
        "option"
    )[1:]

    final_links = []
    for raw_state in states:
        state = raw_state["value"]
        main_link = (
            "https://www.esportafitness.com/Pages/findclubresultszip.aspx?state="
            + state
        )
        logger.info(main_link)

        driver.get(main_link)
        time.sleep(randint(2, 4))

        WebDriverWait(driver, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, ".TextDataColumn"))
        )
        time.sleep(randint(2, 4))

        count = 0
        while True and count < 5:
            base = BeautifulSoup(driver.page_source, "lxml")
            main_items = base.find_all(class_="TextDataColumn")
            for main_item in main_items:
                main_link = (
                    "https://www.esportafitness.com/Pages/" + main_item.a["href"]
                )
                final_links.append(main_link)
            try:
                driver.find_element_by_id("ctl00_MainContent_lnkNextTop").click()
                time.sleep(randint(4, 6))
                count += 1
            except:
                break

    data = []
    total_links = len(final_links)
    for i, final_link in enumerate(final_links):
        logger.info("Link %s of %s" % (i + 1, total_links))
        logger.info(final_link)
        final_req = session.get(final_link, headers=headers)
        item = BeautifulSoup(final_req.text, "lxml")

        locator_domain = "esportafitness.com"

        location_name = item.h1.text.strip()
        try:
            street_address = item.find(id="ctl00_MainContent_lblClubAddress").text
        except:
            continue
        city = item.find(id="ctl00_MainContent_lblClubCity").text
        state = item.find(id="ctl00_MainContent_lblClubState").text
        zip_code = item.find(id="ctl00_MainContent_lblZipCode").text
        country_code = "US"
        store_number = re.findall("clubid=[0-9]+", final_link)[0].split("=")[1].strip()
        location_type = "<MISSING>"
        phone = item.find(id="ctl00_MainContent_lblClubPhone").text
        if "Reg" in phone:
            phone = phone[: phone.find("Reg")].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        hours_of_operation = (
            item.find(id="divClubHourPanel")
            .get_text(" ")
            .replace("pm", "pm ")
            .replace("CLUB HOURS", "")
            .strip()
        )

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

    try:
        driver.close()
    except:
        pass

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
