from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests import SgRequests
import dirtyjson as json

logger = SgLogSetup().get_logger("waterfields")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.waterfields-bakers.co.uk"
base_url = "https://stockist.co/api/v1/u11217/locations/all.js?callback=_stockistAllStoresCallback"


def fetch_records(http):
    locations = json.loads(
        http.get(base_url, headers=_headers)
        .text.split("_stockistAllStoresCallback(")[1]
        .strip()[:-1]
    )
    for _ in locations:
        street_address = _["address_line_1"]
        if _.get("address_line_2"):
            street_address += " " + _["address_line_2"]
        hours = []
        for hh in _.get("custom_fields", []):
            hours.append(f"{hh['name']}: {hh['value']}")

        yield SgRecord(
            page_url="https://www.waterfields-bakers.co.uk/branchfinder",
            store_number=_["id"],
            location_name=_["name"],
            street_address=street_address,
            city=_["city"],
            state=_["state"],
            zip_postal=_["postal_code"],
            country_code=_["country"],
            phone=_["phone"],
            latitude=_["latitude"],
            longitude=_["longitude"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
        )


if __name__ == "__main__":
    with SgRequests() as http:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
            for rec in fetch_records(http):
                writer.write_row(rec)
