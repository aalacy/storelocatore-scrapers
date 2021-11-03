import time
import json
from sgselenium import SgChrome

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sglogging import sglog

import ssl

ssl._create_default_https_context = ssl._create_unverified_context
MISSING = SgRecord.MISSING
locator_domain = "buddyrents.com"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():

    start_url = "https://www.buddyrents.com/storelocator/storelocator_data.php?origLat=37.09024&origLng=-95.712891&origAddress=5000+Estate+Enighed%2C+Independence%2C+KS+67301%2C+%D0%A1%D0%A8%D0%90&formattedAddress=&boundsNorthEast=&boundsSouthWest="

    with SgChrome(is_headless=True, user_agent=user_agent) as driver:
        driver.get(start_url)
        time.sleep(15)
        locs = json.loads(driver.find_element_by_css_selector("body").text)

    for poi in locs:
        page_url = poi["web"]
        if page_url is None:
            page_url = MISSING
        location_name = poi["name"]
        street_address = poi["address"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postal"]
        country_code = "US"
        store_number = poi["id"]
        phone = poi["phone"]
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = f'{poi["hours1"]} {poi["hours2"]} {poi["hours3"]}'

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info(f"Start Crawling {locator_domain} ...")
    result = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)

    log.info("Data Grabbing Finished!!")


if __name__ == "__main__":
    scrape()
