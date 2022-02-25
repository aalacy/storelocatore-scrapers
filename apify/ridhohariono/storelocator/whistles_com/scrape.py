from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import re


DOMAIN = "whistles.com"
BASE_URL = "https://www.whistles.com"
LOCATION_URL = "https://whistles.com/ally-fashion-stores"
API_URL = "https://www.whistles.com/on/demandware.store/Sites-WH-UK-Site/en/Stores-FindStores?lat={}&long={}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.BRITAIN,
            SearchableCountries.HONG_KONG,
            SearchableCountries.IRELAND,
            SearchableCountries.AUSTRALIA,
        ],
        expected_search_radius_miles=50,
        max_search_results=10,
    )
    for lat, long in search:
        data_url = API_URL.format(lat, long)
        log.info(f"Get {search.current_country().upper()} Locations => {data_url}")
        data = session.get(data_url, headers=HEADERS).json()
        for row in data["stores"]:
            search.found_location_at(lat, long)
            page_url = BASE_URL + row["storeUrl"]
            location_name = row["name"]
            street_address = row["address1"]
            try:
                street_address = street_address + " " + row["address2"]
            except:
                pass
            street_address = street_address.split(" at ")[0].strip()
            state = MISSING
            city = row["city"]
            zip_postal = row["postalCode"]
            try:
                phone = re.subr(r"^00", "", row["phone"]).strip()
            except:
                phone = MISSING
            country_code = row["countryCode"]
            if country_code == "US":
                zip_postal = re.sub(r"\D+|-", "", zip_postal).strip()
            hoo = ""
            for day in row["workTimes"]:
                hoo += day["weekDay"] + ": " + day["value"] + ","
            hours_of_operation = hoo.strip().rstrip(",")
            if "Shop 1036" in street_address:
                zip_postal = MISSING
            if "Shop 120A" in street_address:
                city = "Admiralty"
            location_type = row["storeType"]
            if "storeHours" in row and "TEMPORARILY CLOSED" in row["storeHours"]:
                location_type = "TEMPORARILY CLOSED"
            store_number = row["ID"]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
