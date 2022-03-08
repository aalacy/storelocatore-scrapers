import json
from bs4 import BeautifulSoup
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

DOMAIN = "hancockwhitney.com"
LOCATION_URL = "https://locations.hancockwhitney.com/"
API_URL = "https://maps.locations.hancockwhitney.com/api/getAsyncLocations?template=search&radius=1000&level=search&search=36608"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()["maplist"]
    base = BeautifulSoup(data, "lxml")
    js = (
        "["
        + base.text.replace("\r\n", "")
        .replace("\\", "")
        .replace("    ", "")
        .replace(': "{', ": {")
        .replace('}",', "},")[:-1]
        + "]"
    )
    stores = json.loads(js)
    for store_data in stores:
        page_url = store_data["url"]
        location_name = "Hancock Whitney " + store_data["location_name"]
        try:
            street_address = store_data["address_1"] + " " + store_data["address_2"]
        except:
            street_address = store_data["address_1"]
        city = store_data["city"]
        state = store_data["region"]
        zip_postal = store_data["post_code"]
        country_code = store_data["country"]
        store_number = store_data["lid"]
        phone = store_data["local_phone"]
        location_type = store_data["Type_CS"]
        latitude = store_data["lat"]
        longitude = store_data["lng"]
        hours = ""
        try:
            raw_days = store_data["hours_sets:primary"]["days"]
        except:
            hours = MISSING
        if not hours:
            for day in raw_days:
                hour = raw_days[day]
                try:
                    if hour == "closed":
                        clean_hours = day + " " + hour.title()
                    else:
                        opens = hour[0]["open"]
                        closes = hour[0]["close"]
                        clean_hours = day + " " + opens + "-" + closes
                    hours = (hours + " " + clean_hours).strip()
                except:
                    try:
                        hours = (hours + " " + day + " " + hour).strip()
                    except:
                        hours = "SOME OFF"
        log.info("Append {} => {}".format(store_data["location_name"], street_address))
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
            hours_of_operation=hours,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    fetch_data()
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
