from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


DOMAIN = "laporchetta.com.au"
BASE_URL = "https://www.laporchetta.com.au"
LOCATION_URL = "https://laporchetta.com.au/locations/"
API_URL = "https://laporchetta.com.au/wp-admin/admin-ajax.php?action=store_search&lat=-37.81363&lng=144.96306&max_results=25000&search_radius=50000&autoload=1"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        if DOMAIN in row["url"]:
            page_url = row["url"]
        else:
            page_url = BASE_URL + row["url"]
        location_name = row["store"]
        street_address = f"{row['address']}, {row['address2']}".strip().rstrip(",")
        city = row["city"]
        state = row["state"]
        zip_postal = row["zip"]
        store_number = row["id"]
        phone = row["phone"]
        country_code = row["country"]
        location_type = MISSING
        latitude = row["lat"]
        longitude = row["lng"]
        if not row["hours"]:
            hours_of_operation = MISSING
        else:
            hours_of_operation = (
                bs(row["hours"], "lxml")
                .get_text(strip=True, separator=",")
                .replace("day,", "day: ")
            )
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
