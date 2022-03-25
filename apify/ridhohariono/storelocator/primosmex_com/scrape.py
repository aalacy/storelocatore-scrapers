from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re


DOMAIN = "primosmex.com"
LOCATION_URL = "https://primosmex.com/restaurants/"
API_COUNTIES = "https://primosmex.com/api/om/counties"
API_STORES = (
    "https://primosmex.com/api/om/pickupPoints?countyId={}&pageSize=50&isActive=true"
)
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    counties = session.get(API_COUNTIES, headers=HEADERS).json()
    for county in counties:
        store_url = API_STORES.format(county["id"])
        stores = session.get(store_url, headers=HEADERS).json()
        for store in stores["data"]:
            location_name = store["name"]
            if store["address"]["address2"]:
                street_address = (
                    store["address"]["address1"] + " " + store["address"]["address2"]
                ).strip()
            else:
                street_address = store["address"]["address1"].strip()
            city = store["address"]["city"]
            state = store["address"]["state"]["stateCode"]
            if "Aliso Viejo" in location_name:
                city = "Aliso Viejo"
                street_address = street_address.replace(city, "")
            zip_postal = store["address"]["zip"].replace(state, "").strip()
            phone = store["phone"].strip()
            country_code = store["address"]["country"]["countryIATACode"]
            hoo = ""
            for hday in store["pickupHours"]:
                hoo += hday["name"].strip() + ", "
            hours_of_operation = re.sub(r", Dining room.*", "", hoo.strip().rstrip(","))
            location_type = MISSING
            store_number = store["id"]
            latitude = store["lat"]
            longitude = store["lng"]
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
