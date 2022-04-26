from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


URL = "https://api.pressedjuicery.com/stores?sort=name"
DOMAIN = "pressedjuicery.com"

session = SgRequests()

HEADERS = {
    "Host": "api.pressedjuicery.com",
    "Origin": "https://api.pressedjuicery.com/stores?sort=name",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def parse_hours(store):
    ret = []
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for i in range(7):
        start_time = store[days[i]]["start"]
        end_time = store[days[i]]["end"]
        if start_time is not None and end_time is not None:
            if int(str(start_time)[:2]) > 12:
                start = (
                    "0"
                    + str(store[days[i]]["start"])[:1]
                    + ":"
                    + str(store[days[i]]["start"])[1:]
                )
            else:
                start = (
                    str(store[days[i]]["start"])[:2]
                    + ":"
                    + str(store[days[i]]["start"])[2:]
                )
            close = (
                str(store[days[i]]["end"])[:2] + ":" + str(store[days[i]]["end"])[2:]
            )
            day = days[i]
            ret.append("{}: {}-{}".format(day, start, close))
        else:
            day = days[i]
            ret.append("{}: CLOSED".format(day))

    return ", ".join(ret)


def fetch_data():
    log.info("Fetching store_locator data")
    stores = session.get(URL, headers=HEADERS).json()["stores"]
    for store in stores:
        location_name = store["name"]
        street_address = store["streetAddress"]
        city = store["locality"]
        state = store["region"]
        zip_postal = store["postal"]
        country_code = store["country"]
        store_number = store["number"]
        phone = store["phone"]
        location_type = MISSING
        latitude = store["geometry"]["coordinates"][1]
        longitude = store["geometry"]["coordinates"][0]
        hours_of_operation = parse_hours(store["storeHours"])
        page_url = f"https://pressed.com/pages/location-details?id={store['id']}&coordinates={longitude}&coordinates={latitude}"
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
