from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from datetime import datetime

DOMAIN = "ocharleys.com"
BASE_URL = "https://orderback.ocharleys.com"
LOCATION_URL = "https://order.ocharleys.com/?location=true"
API_URL = "https://orderback.ocharleys.com:8081/restaurants"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def parse_hours(row):
    hoo = row["calendars"][0]["ranges"][0]
    start = datetime.strptime(hoo["start"].split()[1], "%H:%M")
    end = datetime.strptime(hoo["end"].split()[1], "%H:%M")
    return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"


def fetch_data():
    log.info("Fetching store_locator data")
    store_info = session.get(API_URL, headers=HEADERS).json()
    for row in store_info["restaurants"]:
        location_name = row["name"]
        street_address = row["streetaddress"]
        city = row["city"]
        state = row["state"]
        zip_code = row["zip"]
        phone = row["telephone"]
        hours_of_operation = parse_hours(row)
        store_number = row["id"]
        country_code = row["country"]
        location_type = row["brand"]
        latitude = row["latitude"]
        longitude = row["longitude"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_code.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
            raw_address=f"{street_address}, {city}, {state} {zip_code} ",
        )


def scrape():
    log.info("asdasStasdasart {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
