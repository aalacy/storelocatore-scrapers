from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()
website = "verlo_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://verlo.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
        )
        for lat, long in search:
            search_url = (
                "https://verlo.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=500&search_radius=1000"
            ).format(lat, long)
            loclist = session.get(search_url, headers=headers).json()
            for loc in loclist:
                page_url = loc["permalink"]
                location_name = loc["store"]
                log.info(page_url)
                store_number = loc["id"]
                phone = loc["phone"]
                street_address = loc["address"]
                city = loc["city"]
                state = loc["state"]
                zip_postal = loc["zip"]
                latitude = loc["lat"]
                longitude = loc["lng"]
                country_code = loc["country"]
                hours_of_operation = loc["hours"]
                hours_of_operation = (
                    BeautifulSoup(hours_of_operation, "html.parser")
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://verlo.com/store-locator/",
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.StoreNumberId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
