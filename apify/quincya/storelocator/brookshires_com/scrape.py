from bs4 import BeautifulSoup

from sglogging import sglog

from sgselenium.sgselenium import SgChrome

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger(logger_name="brookshires.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.brookshires.com/stores/?coordinates=33.081696254439834,-95.94856100000001&zoom=4"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    with SgChrome(user_agent=user_agent) as driver:
        driver.get(base_link)
        base = BeautifulSoup(driver.page_source, "lxml")
        log.info(base)

        sgw.write_row(
            SgRecord(
                locator_domain="",
                page_url=base_link,
                location_name="",
                street_address="",
                city="",
                state="",
                zip_postal="",
                country_code="",
                store_number="",
                phone="",
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation="",
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
