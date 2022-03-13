from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "strandbags.com.au"
LOCATION_URL = "https://www.strandbags.com.au/pages/store-locator"
API_URL = "https://stockist.co/api/v1/u8518/locations/all.js"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        location_name = row["name"]
        street_address = re.sub(
            r".*Centre,", "", row["address_line_2"], flags=re.IGNORECASE
        )
        city = row["city"]
        state = row["state"]
        zip_postal = row["postal_code"]
        country_code = "AU" if row["country"] == "Australia" else row["country"]
        phone = row["phone"].replace("()", "").strip()
        location_type = MISSING
        hours_of_operation = (
            row["description"].replace("OPENING HOURS \n", "").replace(" \n", ",")
        )
        if hours_of_operation == "Mon: -,Tue: -,Wed: -,Thu: -,Fri: -,Sat: -,Sun: -":
            hours_of_operation = MISSING
        store_number = row["id"]
        latitude = row["latitude"]
        longitude = row["longitude"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
