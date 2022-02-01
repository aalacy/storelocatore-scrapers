from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://toysrus.com.ph"
base_url = "https://toysrus.com.ph/stores"
json_url = "https://toysrus.com.ph/stores/fetch"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url, timeout=30)
        locations = json.loads(rr.response.body)["stores"]
        for _ in locations:
            addr = parse_address_intl(_["address"] + ", Philippines")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if not street_address:
                street_address = _["address"]
            city = addr.city or ""
            if city in ["Uno", "Center", "Highwa", "Poblacion District", "Rh9", "Road"]:
                city = ""
            yield SgRecord(
                page_url=base_url,
                store_number=_["store_code"],
                location_name=_["name"],
                street_address=street_address,
                city=city.replace("Brgy. 1", ""),
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Philippines",
                phone=_["contact_number"],
                locator_domain=locator_domain,
                hours_of_operation=_["open_days"].strip().replace("\n", ";"),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
