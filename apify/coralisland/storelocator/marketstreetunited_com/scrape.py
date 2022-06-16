import json
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium import SgChrome
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

website = "marketstreetunited.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    url = "https://www.marketstreetunited.com/RS.Relationshop/StoreLocation/GetAllStoresPosition"

    with SgChrome() as driver:

        driver.get(url)
        stores_sel = lxml.html.fromstring(driver.page_source)
        store_list = json.loads("".join(stores_sel.xpath("//body//text()")).strip())
        for store in store_list:
            if not store["Address1"] and not store["City"]:
                continue
            locator_domain = website
            page_url = "https://www.marketstreetunited.com/rs/StoreLocator?id={}"
            location_name = store["StoreName"]
            street_address = store["Address1"]
            if store["Address2"] and len(store["Address2"]) > 0:
                street_address = street_address + ", " + store["Address2"]
            city = store["City"]
            state = store["State"]
            zip = store["Zipcode"]
            country_code = "US"
            store_number = store["StoreID"]
            page_url = page_url.format(str(store_number))
            phone = store["PhoneNumber"]
            location_type = "<MISSING>"
            latitude = store["Latitude"]
            longitude = store["Longitude"]
            hours_of_operation = store["StoreHours"]
            yield SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
