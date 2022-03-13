import ssl
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data(sgw: SgWriter):

    base_link = "https://www.wingiton.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    time.sleep(10)
    driver.switch_to.frame(driver.find_element_by_tag_name("iframe"))
    time.sleep(2)
    for i in range(7):
        driver.find_element_by_id("zoom-out-btn").click()
        time.sleep(2)

    base = BeautifulSoup(driver.page_source, "lxml")
    driver.close()

    items = base.find(id="location-cards").find_all(class_="card-body")

    for item in items:
        if "coming soon" in item.text.lower():
            continue

        locator_domain = "https://www.wingiton.com"
        location_name = item.h5.text
        raw_data = item.find(class_="col-12").text.split(",")
        street_address = raw_data[0].strip()
        city = location_name.split(",")[0]
        state = location_name.split(",")[1].split("-")[0].strip()
        if len(raw_data) > 1:
            zip_code = raw_data[-1].replace(state, "").strip()
            if "US" in zip_code:
                zip_code = raw_data[-2].replace(state, "").strip()
        else:
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = item.a.text
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            item.find_all(class_="col-10 ml-1 p-0")[-1]
            .text.replace("\n", " ")
            .replace("Hours of Operation:", "")
            .strip()
        )

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=base_link,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
