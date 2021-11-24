from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "woolworths.com.au"
LOCATION_URL = "https://www.woolworths.com.au/shop/storelocator"
API_URL = "https://www.woolworths.com.au/apis/ui/StoreLocator/Stores?Max=100000&Division=SUPERMARKETS,PETROL,CALTEXWOW,METROCALTEX&Facility=&latitude=-33.865143&longitude=151.2099"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data["Stores"]:
        location_name = row["Name"]
        if row["AddressLine2"]:
            street_address = row["AddressLine1"] + " " + row["AddressLine2"]
        else:
            street_address = row["AddressLine1"]
        street_address = " ".join(street_address.split())
        city = row["Suburb"]
        state = row["State"]
        zip_postal = row["Postcode"]
        phone = row["Phone"]
        country_code = "AU"
        store_number = row["StoreNo"]
        hoo = ""
        for hday in row["TradingHours"]:
            hoo += hday["Day"] + ": " + hday["OpenHour"] + ","
        hours_of_operation = hoo.rstrip(",")
        latitude = row["Latitude"]
        longitude = row["Longitude"]
        location_type = row["Division"]
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
