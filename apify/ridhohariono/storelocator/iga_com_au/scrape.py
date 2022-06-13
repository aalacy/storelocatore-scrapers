import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicZipAndGeoSearch, Grain_1_KM

DOMAIN = "iga.com.au"
BASE_URL = "https://www.iga.com.au/stores/#view=storelocator"
API_URL = "https://embed.salefinder.com.au/location/search/183/?sensitivity=5&noStoreSuffix=1&withStoreInfo=1&query={}"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json; charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = SgRecord.MISSING
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicZipAndGeoSearch(
        country_codes=[SearchableCountries.AUSTRALIA],
        expected_search_radius_miles=0.2,
        granularity=Grain_1_KM(),
        max_search_results=5,
    )
    for zipcode, coord in search:
        lat, long = coord
        url = API_URL.format(zipcode)
        log.info("Pull content => " + url)
        stores = json.loads(
            session.get(url, headers=HEADERS).text.replace("({", "{").replace("})", "}")
        )
        if not stores["result"]:
            search.found_nothing()
            continue
        search.found_location_at(lat, long)
        for row in stores["result"]:
            location_name = row["storeName"]
            street_address = (
                row["address"].replace("\r\n", "").replace("\n", "").strip()
            )
            city = row["suburb"]
            state = row["state"]
            zip_postal = row["postcode"]
            phone = row["phone"]
            country_code = "AU"
            store_number = row["storeId"]
            location_type = MISSING
            hoo = ""
            try:
                hours = row["hours"].replace("\r\n", "\n").split("\n")
                days = row["hoursDay"].replace("\r\n", "\n").split("\n")
                for i in range(len(days)):
                    hoo += days[i] + ": " + hours[i] + ", "
                hours_of_operation = hoo.strip().rstrip(",").strip().rstrip(":")
            except:
                hours_of_operation = MISSING
            latitude = row["latitude"]
            longitude = row["longitude"]
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=BASE_URL,
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
