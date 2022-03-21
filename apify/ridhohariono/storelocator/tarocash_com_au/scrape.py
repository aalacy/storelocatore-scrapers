from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "tarocash.com.au"
BASE_URL = "https://www.tarocash.com.au/au/store/"
API_URL = "https://mcprod2.tarocash.com.au/graphql?query=query+storeLocations%28%24location%3ALocationRequest%24pageSize%3AInt%3D2000%24currentPage%3AInt%3D1%29%7Bstockists%28location%3A%24location+pageSize%3A%24pageSize+currentPage%3A%24currentPage%29%7Bcanonical_url+locations%7Baddress%7Bcity+country_code+phone+postcode+region+street+suburb+__typename%7Didentifier+location%7Blat+lng+__typename%7Dname+trading_hours%7Bsunday+monday+tuesday+wednesday+thursday+friday+saturday+public_holidays+__typename%7Durl_key+__typename%7Dmw_hreflangs%7Bitems%7Burl+code+__typename%7D__typename%7D__typename%7D%7D&operationName=storeLocations&variables=%7B%22pageSize%22%3A20%2C%22currentPage%22%3A1%2C%22location%22%3A%7B%22lat%22%3A-21.7732804%2C%22lng%22%3A132.1878186%2C%22radius%22%3A500000000%7D%7D"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "store": "tc_au",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()["data"]["stockists"]
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for row in data["locations"]:
        page_url = BASE_URL + row["url_key"]
        location_name = row["name"]
        address = row["address"]
        street_address = address["street"]
        city = address["suburb"]
        state = MISSING
        zip_postal = address["postcode"]
        country_code = address["country_code"]
        phone = address["phone"]
        latitude = row["location"]["lat"]
        longitude = row["location"]["lng"]
        hoo = ""
        for day in days:
            hour = row["trading_hours"][day] or "Closed"
            hoo += day.title() + ": " + hour + ", "
        hours_of_operation = hoo.strip().rstrip(",")
        location_type = MISSING
        if "TEMPORARILY CLOSED" in hours_of_operation:
            location_type = "TEMPORARILY CLOSED"
            hours_of_operation = "TEMPORARILY CLOSED"
        store_number = row["identifier"].replace("TC-", "").strip()
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
