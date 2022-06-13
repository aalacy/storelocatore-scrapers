from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sgpostal.sgpostal import parse_address_intl
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

locator_domain = "https://www.sallymexico.com"
base_url = "https://www.sallymexico.com/stores"
json_url = r"https://www.sallymexico.com/api/dataentities/WH/scroll"
asset_url = r"https://e.clarity.ms/collect"


def fetch_data():
    with SgChrome(
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    ) as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url, timeout=15)
        hours = [
            "lunes a sábado 9am a 8pm",
            "Domingo 9am a 5pm",
        ]
        locations = json.loads(rr.response.body)
        for _ in locations:
            street_address = _["address"]
            if _["city"] in street_address or _["stateCode"] in street_address:
                addr = parse_address_intl(_["address"] + ", Mexico")
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address.replace("\n", " "),
                city=_["city"],
                state=_["stateCode"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"].replace(",", "."),
                longitude=_["longitude"].replace(",", "."),
                country_code="Mexico",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
