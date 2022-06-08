from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "lotaburger.com"
LOCATION_URL = "http://www.lotaburger.com/ResTuarant"
API_URL = "https://www.lotaburger.com/wp-json/ip/v1/blakes_location_json/"
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
        page_url = row["business_url"]
        location_name = "Store #" + row["store_number"]
        street_address = row["business_address"]
        city = row["business_city"]
        state = row["business_state"]
        zip_postal = row["business_zipcode"]
        country_code = "US"
        phone = row["business_phone"]
        hoo = ""
        for hday in row["store_hours"]:
            if hday["hours"][0]["closed"]:
                hours = "Closed"
            else:
                hours = hday["hours"][0]["from"] + " - " + hday["hours"][0]["to"]
            hoo += hday["day"] + ": " + hours + ", "
        hours_of_operation = hoo.strip().rstrip(",")
        location_type = MISSING
        store_number = row["store_number"]
        latitude = row["coords"]["lat"]
        longitude = row["coords"]["long"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
