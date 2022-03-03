from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("lagranjarestaurants")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://lagranjarestaurants.com"
base_url = "https://lagranjarestaurants.com/en/locations/index.php"


def fetch_data():
    with SgRequests() as http:
        soup = bs(http.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.w-item.lanza-direccion")
        logger.info(f"{len(locations)} found")
        for _ in locations:
            coord = _["data-coor"].split(",")
            raw_address = " ".join(list(_.select_one("div.w-text1").stripped_strings))
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=base_url,
                store_number=_["data-position"],
                location_name=_["data-name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_["data-phone"],
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
