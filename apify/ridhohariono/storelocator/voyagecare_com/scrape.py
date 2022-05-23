from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "voyagecare.com"
BASE_URL = "https://voyagecare.com/"
LOCATION_URL = "https://www.voyagecare.com/in-your-area"
API_URL = "https://www.voyagecare.com/wp-json/voyagecare/v1/services/0/0/0/0/0/0/0"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data["body"]:
        page_url = BASE_URL + row["properties"]["route"]
        location_name = row["properties"]["post_title"]
        if not row["properties"]["address1_line2"]:
            try:
                street_address = (
                    row["properties"]["address1_line1"].replace("\n", " ").strip()
                ) or MISSING
            except:
                street_address = MISSING
        else:
            street_address = (
                (
                    row["properties"]["address1_line1"]
                    + ", "
                    + row["properties"]["address1_line2"]
                )
                .replace("\n", " ")
                .strip()
            )
        city = row["properties"]["address1_city"] or MISSING
        state = MISSING
        zip_postal = row["properties"]["address1_postalcode"] or MISSING
        if zip_postal != MISSING:
            if len(zip_postal.split(" ")) < 2 or len(zip_postal) > 9:
                city = zip_postal
                zip_postal = MISSING
        phone = MISSING
        country_code = "UK"
        hours_of_operation = MISSING
        store_number = row["properties"]["id"]
        location_type = row["properties"]["new_voyageservicetype"]
        latitude = row["properties"]["address1_latitude"]
        longitude = row["properties"]["address1_longitude"]
        log.info("Append {} => {}, {}".format(location_name, street_address, city))
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
