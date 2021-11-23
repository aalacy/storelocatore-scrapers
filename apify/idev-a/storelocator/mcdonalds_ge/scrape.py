from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mcdonalds.ge"
base_url = "https://mcdonalds.ge/api/locations/?all=true&isFeatured=true"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["items"]
        for _ in locations:
            addr = parse_address_intl(_["address"]["en"] + ", Georgia")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            _addr = [aa.strip() for aa in _["address"]["en"].split(",")]
            city = addr.city
            if len(_addr) > 1:
                if len(_addr[0].split(" ")) == 1:
                    city = _addr[0]
                    street_address = " ".join(_addr[1:])
                elif len(_addr[1].split(" ")) == 1:
                    city = _addr[1]
                    street_address = _addr[0]
            hours = []
            if _["description"]["ge"]:
                hours = list(bs(_["description"]["ge"], "lxml").stripped_strings)
                if hours:
                    hours = hours[1:]
            yield SgRecord(
                page_url="https://mcdonalds.ge/location",
                location_name=_["name"]["en"],
                street_address=street_address,
                city=city,
                latitude=_["location"]["coordinates"][0],
                longitude=_["location"]["coordinates"][1],
                country_code="Georgia",
                phone=_.get("phoneNumber"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"]["en"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
