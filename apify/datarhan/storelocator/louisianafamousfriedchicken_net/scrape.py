import json
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "louisianafamousfriedchicken.net"
API_URL = "https://louisianafriedchickenhq.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=500&autoload=1"
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=500
    )
    for lat, lng in all_coords:
        log.info("Pull content => " + API_URL.format(lat, lng))
        response = session.get(API_URL.format(lat, lng))
        data = json.loads(response.text)
        for poi in data:
            store_url = poi["permalink"]
            location_type = MISSING
            hours_of_operation = poi["hours"]
            hours_of_operation = hours_of_operation if hours_of_operation else MISSING
            location_name = poi["store"]
            location_name = location_name if location_name else "<MISSING"
            street_address = poi["address"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["zip"]
            if len(zip_code) > 5:
                zip_code = MISSING
            country_code = poi["country"]
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else MISSING
            latitude = poi["lat"]
            longitude = poi["lng"]
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
