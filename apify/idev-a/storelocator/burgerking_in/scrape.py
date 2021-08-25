from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
import time
from sglogging import SgLogSetup
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger("burgerking")

locator_domain = "https://www.burgerking.in"
base_url = "https://www.burgerking.in/store-locator"
json_url = "/api/v1/outlet/getOutlet"


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1"
    ) as driver:
        try:
            driver.get(base_url)
        except:
            pass
        try:
            driver.switch_to.alert.accept()
        except:
            pass
        driver.get(base_url)
        try:
            driver.wait_for_request(json_url, 30)
        except:
            pass
        try:
            driver.wait_for_request(json_url, 30)
        except:
            pass
        data = []
        while True:
            data = [rr.response for rr in driver.requests if json_url in rr.url]
            time.sleep(1)
            if len(data) > 1 and data[1]:
                break
            logger.info("--- waiting ---")
        locations = json.loads(data[-1].body)["content"]
        logger.info(f"{len(locations)} found")
        for _ in locations:
            if _["is_closed"]:
                continue
            addr = parse_address_intl(_["address"] + ", India")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = f"{_['opens_at']}-{_['closes_at']}"
            yield SgRecord(
                page_url="https://www.burgerking.in/store-locator",
                store_number=_["outlet_id"],
                location_name=_["outlet_name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["long"],
                country_code="India",
                phone=_["phone_no"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
