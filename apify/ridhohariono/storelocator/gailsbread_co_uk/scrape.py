from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import re

MISSING = "<MISSING>"

DOMAIN = "gailsbread.co.uk"
API_URL = "https://gailsbread.co.uk/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=50&search_radius=300"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        expected_search_radius_miles=300,
        max_search_results=50,
    )
    for lat, long in search:
        url = API_URL.format(lat, long)
        log.info(f"Pull data from => {url}")
        stores = session.get(url, headers=HEADERS).json()
        for store in stores:
            search.found_location_at(lat, long)
            page_url = store["permalink"]
            location_name = store["store"].replace("&#8217;", "'")
            street_address = (store["address"] + " " + store["address2"]).strip()
            city = store["city"] or MISSING
            state = store["state"] or MISSING
            zip_postal = store["zip"] or MISSING
            if zip_postal == MISSING:
                zip = street_address.split(",")[-1].strip()
                if len(zip) > 5 and len(zip) <= 8 and len(zip.split(" ")) > 1:
                    zip_postal = zip
                if (
                    store["country"] != "United Kingdom"
                    and len(store["country"]) > 5
                    and len(store["country"]) <= 8
                    and len(store["country"].split(" ")) > 1
                ):
                    zip_postal = store["country"]
            street_address = re.sub(
                r",?\s?" + city + r"|,?\s?" + zip_postal, "", street_address
            )
            country_code = "UK"
            phone = store["phone"]
            hours_of_operation = (
                bs(store["hours"], "lxml")
                .get_text(strip=True, separator=",")
                .replace("day,", "day: ")
                .strip()
            ) or MISSING
            location_type = MISSING
            store_number = store["id"]
            latitude = store["lat"]
            longitude = store["lng"]
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
