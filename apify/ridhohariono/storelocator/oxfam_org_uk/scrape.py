from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

DOMAIN = "oxfam.com"
API_URL = "https://www.oxfam.org.uk/api/locations/?query="
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def fetch_data():
    log.info("Fetching store_locator data")
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_search_distance_miles=100,
    )
    for zipcode in search:
        url = API_URL + zipcode.replace(" ", "+")
        try:
            data = session.get(url, headers=HEADERS).json()["results"]
        except:
            continue
        log.info(f"Found {len(data)} locations from => {url}")
        for row in data:
            if not row["shop"]:
                continue
            info = row["shop"]
            page_url = info["detail_url"]
            location_name = info["name"].replace("&#039;", "'")
            if "Coming Soon" in location_name:
                continue
            street_address = (
                info["address_line_1"]
                + " "
                + info["address_line_2"]
                + " "
                + info["address_line_3"]
            ).strip()
            city = info["town"]
            state = MISSING
            zip_postal = info["postcode"]
            phone = info["phone_number"]["international"]
            country_code = "UK"
            store_number = info["id"]
            hours_of_operation = MISSING
            latitude = row["geolocation"]["latitude"]
            longitude = row["geolocation"]["longitude"]
            location_type = MISSING
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
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumAndPageUrlId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
