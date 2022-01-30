from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://carrefourtunisie.com"
base_url = "https://www.carrefour.tn/rest/all/V1/carrefour/stores"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
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
                _["working_hours"]
                + " de "
                + _["starting_hour"]
                + " à "
                + _["closing_hour"]
            )
            yield SgRecord(
                page_url="https://www.carrefour.tn/default/nos-magasins",
                store_number=_["our_store_id"],
                location_name=_["name"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["lat"],
                longitude=_["long"],
                country_code="Tunisia",
                location_type=_["format"],
                locator_domain=locator_domain,
                hours_of_operation=hours,
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
