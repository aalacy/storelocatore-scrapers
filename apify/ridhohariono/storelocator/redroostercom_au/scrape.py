from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "redrooster.com.au"
LOCATION_URL = "https://www.redrooster.com.au/locations/"
API_URL = "https://www.redrooster.com.au/api/stores/1/"
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
        page_url = LOCATION_URL + row["slug"]
        if not row["address"] and not row["suburb"]:
            continue
        location_name = row["title"]
        street_address = row["address"].replace("\n", ",")
        city = row["suburb"]
        state = row["state"]
        zip_postal = row["postcode"]
        phone = row["phone"]
        country_code = "AU"
        store_number = row["storeNumber"]
        hoo = ""
        for key, val in row["opening_hours"].items():
            if not val:
                hours = "Closed"
            else:
                hours = val["open"] + " - " + val["close"]
            hoo += key.title() + ": " + hours + ","
        hours_of_operation = hoo.rstrip(",").strip()
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
