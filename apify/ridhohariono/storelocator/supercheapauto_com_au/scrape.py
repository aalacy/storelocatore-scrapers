from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

DOMAIN = "supercheapauto.com.au"
LOCATION_URL = "https://www.supercheapauto.com.au/pages/store-locator"
API_URL = "https://www.supercheapauto.com.au/on/demandware.store/Sites-supercheap-au-Site/en_AU/Stores-SearchPost"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
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
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.AUSTRALIA],
        expected_search_radius_miles=50,
        max_search_results=30,
    )
    for lat, long in search:
        payload = {"lat": lat, "lng": long, "countryCode": "AU"}
        data = session.post(API_URL, headers=HEADERS, data=payload).json()
        for row in data["stores"]:
            search.found_location_at(lat, long)
            page_url = row["storeDetailURL"]
            location_name = row["name"]
            street_address = (row["address1"] + " " + row["address2"]).strip()
            city = row["city"]
            state = row["stateCode"]
            zip_postal = row["postalCode"]
            country_code = "AU"
            phone = row["phone"]
            store = pull_content(page_url)
            hours_of_operation = (
                store.find("div", {"class": "opening-hours"})
                .find("dl")
                .get_text(strip=True, separator=" ")
            )
            location_type = MISSING
            store_number = MISSING
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
