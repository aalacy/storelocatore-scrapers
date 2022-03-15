import json
import ssl

from bs4 import BeautifulSoup

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

    base_link = "https://www.menards.com/store-details/locator.html"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    base = BeautifulSoup(driver.page_source, "lxml")

    locator_domain = "menards.com"

    js = base.find(id="initialStores")["data-initial-stores"]
    stores = json.loads(js)

    for store in stores:
        location_name = store["name"]
        street_address = store["street"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zip"]
        country_code = "US"
        store_number = store["number"]
        phone = "<INACCESSIBLE>"
        hours_of_operation = "<INACCESSIBLE>"
        latitude = store["latitude"]
        longitude = store["longitude"]

        location_type = ""
        loc_types = store["services"]
        for loc_type in loc_types:
            location_type = location_type + ", " + loc_type["displayName"]
        location_type = location_type[1:].strip()

        link = "https://www.menards.com/main/storeDetails.html?store=" + str(
            store_number
        )

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

    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
