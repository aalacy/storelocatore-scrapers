from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("skiclub")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.skiclub.co.uk/"
    base_url = "https://www.skiclub.co.uk/uk-slopes-map"
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("section.module--non-standard.search")[
                "data-skiing-in-the-uk-all"
            ]
            .replace("&quot;", '"')
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            addr = parse_address_intl(_["AddressSummary"].replace(".", "") + ", UK")
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            if not city:
                _addr = _["AddressSummary"].split(",")
                if len(_addr) > 3:
                    city = _addr[-3]
                elif street_address != _addr[-2]:
                    city = _addr[-2]
            if not street_address:
                street_address = _["Name"]
            yield SgRecord(
                page_url=_["Url"],
                location_name=_["Name"],
                street_address=street_address,
                city=city,
                zip_postal=_["Postcode"],
                country_code="UK",
                phone=_["Phone"],
                locator_domain=locator_domain,
                latitude=_["Latitude"],
                longitude=_["Longitude"],
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
