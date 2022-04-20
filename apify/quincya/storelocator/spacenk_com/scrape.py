import re
import ssl
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from sgselenium.sgselenium import SgChrome

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("spacenk_com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://uberall.com/api/storefinders/bdwTQJoL7hB55B0EimfSmXjiMRV8eg/locations/all?v=20211005&language=en&fieldMask=id&fieldMask=identifier&fieldMask=googlePlaceId&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "spacenk.com"

    driver = SgChrome(user_agent=user_agent).driver()

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["response"]["locations"]

    for store in stores:

        location_name = store["name"]
        street_address = store["streetAndNumber"]
        city = store["city"]
        state = store["province"]
        zip_code = store["zip"]
        country_code = store["country"]
        store_number = store["id"]
        location_type = "<MISSING>"
        latitude = store["lat"]
        longitude = store["lng"]
        final_link = (
            "https://www.spacenk.com/us/stores.html#!/l/"
            + city.lower().replace(" ", "-")
            + "/"
            + street_address.lower().replace(" ", "-")
            + "/"
            + str(store_number)
        )

        logger.info(final_link)
        driver.get(final_link)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ubsf_details-details-title")
            )
        )
        time.sleep(2)

        item = BeautifulSoup(driver.page_source, "lxml")

        phone = item.find(class_="ubsf_details-phone").text.strip()
        hours = (
            " ".join(
                list(item.find(class_="ubsf_details-opening-hours").stripped_strings)
            )
            .replace("closed", "")
            .replace("Special Opening Hours", "")
            .strip()
        )

        hours_of_operation = re.sub(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", "", hours)
        hours_of_operation = hours_of_operation.replace("  ", " ").strip()

        if ":0" not in hours_of_operation:
            hours_of_operation = "Closed"

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=final_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
