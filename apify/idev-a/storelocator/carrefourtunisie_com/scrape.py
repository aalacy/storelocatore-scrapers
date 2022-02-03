from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://carrefourtunisie.com"
base_url = "https://www.carrefour.tn/default/nos-magasins"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("let carrefourStores =")[1]
            .split("let")[0]
            .strip()[:-1]
        )
        for _ in locations:
            if not _["address"]:
                continue
            addr = parse_address_intl(_["address"] + ", Tunisia")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address and street_address.isdigit():
                street_address = _["address"]
            city = addr.city
            if city and city.isdigit():
                city = ""

            hours = (
                _["workinghours"]
                + " de "
                + _["startinghour"]
                + " à "
                + _["closinghour"]
            )
            yield SgRecord(
                page_url=base_url,
                store_number=_["storeId"],
                location_name=_["name"],
                street_address=street_address.replace("Carrefour Market", "")
                .replace("Carreour Market", "")
                .replace("Carrefour Express", "")
                .replace("Carreour Express", "")
                .replace("Carrefour Orange", "")
                .replace("Tunisia", ""),
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["lang"],
                country_code="Tunisia",
                location_type=_["type"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
