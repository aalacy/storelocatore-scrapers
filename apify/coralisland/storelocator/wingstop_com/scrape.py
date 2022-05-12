from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()
website = "wingstop_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.wingstop.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
        )
        for lat, lng in search:
            log.info(
                "Searching: %s, %s | Items remaining: %s"
                % (lat, lng, search.items_remaining())
            )
            url = (
                "https://api.wingstop.com/restaurants/near?lat="
                + str(lat)
                + "&long="
                + str(lng)
                + "&radius=100&limit=100"
            )
            loclist = session.get(url, headers=headers).json()["restaurants"]
            for loc in loclist:
                location_name = loc["name"]
                log.info(location_name)
                store_number = loc["id"]
                phone = loc["telephone"]
                street_address = loc["streetaddress"]
                city = loc["city"]
                state = loc["state"]
                zip_postal = loc["zip"]
                latitude = loc["latitude"]
                longitude = loc["longitude"]
                country_code = loc["country"]
                hours_of_operation = "<INACCESSIBLE>"
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://www.wingstop.com/order",
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
