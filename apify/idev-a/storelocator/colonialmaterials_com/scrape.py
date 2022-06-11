from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("colonialmaterials")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.colonialmaterials.com/"
    base_url = "https://www.colonialmaterials.com/Contact.do"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = json.loads(
            soup.select_one("v-select")[":items"].replace("&#34;", '"')
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            page_url = locator_domain + _["aboutUrl"]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postalCode"],
                country_code="US",
                phone=_["phone1"],
                locator_domain=locator_domain,
                latitude=_["latitude"],
                longitude=_["longitude"],
                hours_of_operation=_["weekdayHours"].replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
