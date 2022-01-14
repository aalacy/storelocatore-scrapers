from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "muchoburrito.com"
API_URL = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=GTKDWXDZMLHWYIKP&pageSize=10000"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def format_hours(hours):
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hoo = ""
    hours = hours.split(";")
    num = 0
    for day in days:
        try:
            hour = hours[num].split(",")
        except:
            break
        try:
            start = hour[1][:2] + ":" + hour[1][-2:]
            end = hour[2][:2] + ":" + hour[2][-2:]
            hoo += day + ": " + start + " - " + end + ","
        except:
            hoo += day + ": ClOSED,"
        num += 1
    return hoo.rstrip(",")


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        if row["store_info"]["status"] == "coming soon":
            continue
        elif row["store_info"]["status"] == "closed":
            location_type = "TEMP_CLOSED"
        else:
            location_type = MISSING
        page_url = row["store_info"]["website"]
        location_name = row["store_info"]["name"]
        street_address = (
            (
                row["store_info"]["address"]
                + ", "
                + row["store_info"]["address_extended"]
            )
            .strip()
            .rstrip(",")
        )
        city = row["store_info"]["locality"]
        state = row["store_info"]["region"]
        zip_postal = row["store_info"]["postcode"]
        country_code = row["store_info"]["country"]
        phone = row["store_info"]["phone"]
        store_number = row["store_info"]["corporate_id"]
        if not row["store_info"]["store_hours"]:
            hours_of_operation = MISSING
        else:
            hours_of_operation = format_hours(row["store_info"]["store_hours"])
        latitude = row["store_info"]["latitude"]
        longitude = row["store_info"]["longitude"]
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
