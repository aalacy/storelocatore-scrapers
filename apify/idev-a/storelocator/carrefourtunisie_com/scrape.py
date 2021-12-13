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
base_url = "https://carrefourtunisie.com/api/getAllStores"

type_map = {"CE": "Carrefour Express", "CM": "Carrefour Market", "C": "Carrefour"}


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = parse_address_intl(_["adresse"] + ", Tunisia")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            if street_address and street_address.isdigit():
                street_address = _["adresse"]
            yield SgRecord(
                page_url="https://carrefourtunisie.com/magasins-carrefour",
                store_number=_["idReseau"],
                location_name=_["magasin"],
                street_address=street_address,
                city=_["ville"],
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Tunisia",
                phone=_["tel"],
                location_type=type_map[_["enseigne"]],
                locator_domain=locator_domain,
                hours_of_operation=_["info"],
                raw_address=_["adresse"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
