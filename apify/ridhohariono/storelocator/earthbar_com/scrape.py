from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "earthbar.com"
LOCATION_URL = "https://earthbar.com/pages/store-locator"
API_URL = "https://cdn.shopify.com/s/files/1/0593/4730/4643/t/1/assets/sca.storelocatordata.json?v=1641931269&_=1642448173816"
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
        location_name = row["name"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["postal"]
        street_address = (
            row["address"]
            .replace(city + ",", "")
            .replace(state, "")
            .replace(zip_postal, "")
            .replace("92014", "")
            .strip()
            .rstrip(",")
        )
        if "phone" not in row:
            phone = MISSING
        else:
            phone = row["phone"]
        country_code = "US" if row["country"] == "USA" else row["country"]
        store_number = row["id"]
        location_type = MISSING
        if "schedule" in row:
            hours_of_operation = row["schedule"].replace("\r<br>", ",").strip()
        else:
            hours_of_operation = MISSING
        latitude = row["lat"]
        longitude = row["lng"]
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
