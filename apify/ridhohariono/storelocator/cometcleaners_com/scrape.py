import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch

DOMAIN = "cometcleaners.com"
BASE_URL = "http://cometcleanersfrisco.com/"
LOCATION_URL = "https://www.cometcleaners.com/comet-cleaners-locations/"
API_URL = "https://www.cometcleaners.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results={}&search_radius={}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    max_distance = 500
    max_results = 100
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )
    for lat, long in search:
        url = API_URL.format(str(lat), str(long), max_results, max_distance)
        log.info("Pull data from => " + url)
        stores = json.loads(session.get(url, headers=HEADERS).content)
        for row in stores:
            search.found_location_at(lat, long)
            page_url = row["url"] if row["url"] else LOCATION_URL
            if page_url == BASE_URL:
                page_url = LOCATION_URL
            location_name = row["store"].strip()
            street_address = (row["address"] + " " + row["address2"]).strip()
            city = row["city"]
            state = row["state"]
            zip_postal = row["zip"]
            country_code = "US" if row["country"] == "United States" else row["country"]
            phone = row["phone"]
            store_number = row["id"]
            hours_of_operation = (
                bs(row["hours"], "lxml")
                .get_text(strip=True, separator=", ")
                .replace("day,", "day:")
                .strip()
            )
            location_type = MISSING
            latitude = row["lat"]
            longitude = row["lng"]
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
