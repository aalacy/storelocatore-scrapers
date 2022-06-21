import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

DOMAIN = "louisianafamousfriedchicken.net"
API_URL = "https://louisianafriedchickenhq.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=500&autoload=1"
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
    )
    for lat, lng in all_coords:
        log.info("Pull content => " + API_URL.format(lat, lng))
        response = session.get(API_URL.format(lat, lng))
        if response.status_code != 200:
            continue
        data = json.loads(response.text)
        for poi in data:
            store_url = (
                poi.get("url") or "https://louisianafriedchickenhq.com/locations/"
            )
            hours_of_operation = poi["hours"]
            location_name = poi["store"]
            street_address = poi["address"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["zip"]
            if len(zip_code) > 5:
                zip_code = MISSING
            country_code = poi["country"]
            store_number = poi["id"]
            phone = poi["phone"]
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
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
