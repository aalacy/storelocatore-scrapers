from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "urbanplates.com"
BASE_URL = "https://urbanplates.com/store-details/?store_id={}"
LOCATION_URL = "https://urbanplates.com/location/"
API_URL = "https://urbanplates.com/wp-admin/admin-ajax.php?nonce={}&action=novadine_api_call&method=GET&endpoint=stores%3Fall_stores%3Dtrue"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    content = session.get(LOCATION_URL, headers=HEADERS).text
    nonce = re.search(r"var novadine_nonce = '(.*)'", content).group(1)
    data = session.get(API_URL.format(nonce), headers=HEADERS).json()
    for row in data:
        location_name = row["name"]
        if "Support Center" in location_name:
            continue
        page_url = BASE_URL.format(row["store_id"])
        street_address = row["address1"].strip()
        city = row["city"]
        state = row["state"]
        zip_postal = row["postal_code"]
        phone = row["phone"]
        country_code = row["country"]
        hoo = ""
        for hday in row["hours"]:
            hoo += (
                hday["display_name"]
                + ": "
                + hday["start_time"]
                + "-"
                + hday["end_time"]
                + ","
            )
        hours_of_operation = hoo.strip().rstrip(",")
        store_number = row["store_id"]
        location_type = MISSING
        latitude = row["latitude"]
        longitude = row["longitude"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
