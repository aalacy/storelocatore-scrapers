from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "plowhearth.com"
BASE_URL = "https://www.plowhearth.com"
LOCATION_URL = "https://www.plowhearth.com/en/store-finder?q=-&page={}"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def fetch_data():
    log.info("Fetching store_locator data")
    num = 0
    while True:
        data = session.get(LOCATION_URL.format(num), headers=HEADERS).json()["data"]
        if not data:
            break
        for row in data:
            page_url = (
                (BASE_URL + row["url"]).replace(" ", "%20").replace("&q=-", "").strip()
            )
            location_name = row["displayName"]
            street_address = (row["line1"] + " " + row["line2"]).strip()
            city = row["town"]
            state = row["state"]
            zip_postal = row["postalCode"]
            phone = row["phone"]
            country_code = "US"
            location_type = MISSING
            try:
                hours_of_operation = " ".join(
                    "{} : {}".format(key, value)
                    for key, value in row["openings"].items()
                )
            except:
                hours_of_operation = MISSING
                location_type = "TEMP_CLOSED"
            store_number = MISSING
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
        num += 1


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
