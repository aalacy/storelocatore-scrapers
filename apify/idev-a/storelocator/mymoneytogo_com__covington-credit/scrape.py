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

locator_domain = "https://www.mymoneytogo.com/covington-credit/"
base_url = "https://www.mymoneytogo.com/wp-content/plugins/superstorefinder-wp/ssf-wp-json-wpml.php"
map_url = (
    "https://www.mymoneytogo.com/wp-content/themes/mymoneytogo2020/js/custom-map.js"
)


def fetch_data():
    with SgRequests() as session:
        hours = list(
            bs(
                session.get(map_url, headers=_headers)
                .text.split("<p><strong>Office Hours:</strong>")[1]
                .split('<p class="mb-md-0">')[0],
                "lxml",
            ).stripped_strings
        )
        locations = session.get(base_url, headers=_headers).json()["item"]
        for _ in locations:
            addr = parse_address_intl(_["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            location_type = _["category"][0]
            if "Covington_Credit" != location_type:
                continue
            yield SgRecord(
                page_url=_["exturl"],
                store_number=_["storeId"],
                location_name=_["location"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="USA",
                phone=_["telephone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["address"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
