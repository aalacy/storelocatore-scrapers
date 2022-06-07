import json
import ssl
import time

from bs4 import BeautifulSoup

from sgselenium import SgChrome

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sglogging import sglog

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    log = sglog.SgLogSetup().get_logger(logger_name="spaceagefuel.com")

    base_link = "http://spaceagefuel.com/wp-json/store-locator-plus/v2/locations/"

    with SgChrome() as driver:
        driver.get_and_wait_for_request(base_link)

        log.debug(driver.page_source)

        base = BeautifulSoup(driver.page_source, "lxml")

        sl_ids = json.loads(base.text)

        locator_domain = "spaceagefuel.com"

        for sl_id in sl_ids:
            store_link = base_link + sl_id["sl_id"]

            driver.get(store_link)

            time.sleep(5)
            base = BeautifulSoup(driver.page_source, "lxml")

            log.debug(base.text)

            store = json.loads(base.text)
            location_name = store["sl_store"].replace("amp;", "")
            street_address = (store["sl_address"] + " " + store["sl_address2"]).strip()
            city = store["sl_city"]
            state = store["sl_state"]
            zip_code = store["sl_zip"]
            country_code = "US"
            store_number = store["sl_id"]
            location_type = "<MISSING>"
            phone = store["sl_phone"]
            hours_of_operation = "<MISSING>"
            latitude = store["sl_latitude"]
            longitude = store["sl_longitude"]
            if not latitude:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            link = store["sl_url"]
            if not link:
                link = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
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
