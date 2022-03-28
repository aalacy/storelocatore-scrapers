from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import re
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("pullapart")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pullapart.com"
base_url = "https://externalinterchangeservice.pullapart.com/interchange/GetLocations"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            page_url = f"https://www.pullapart.com/locations/{_['locationName'].lower().replace(' ','-')}/"
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            temp = (
                sp1.find("h2", string=re.compile(r"Retail Sales Hours:"))
                .find_next_sibling("div")
                .stripped_strings
            )
            hours = []
            for hh in temp:
                if "Yard" in hh:
                    break
                if "will be" in hh:
                    continue
                hours.append(hh)
            yield SgRecord(
                page_url=page_url,
                store_number=_["locationID"],
                location_name=_["locationName"],
                street_address=street_address,
                city=_["cityName"],
                state=_["stateName"],
                zip_postal=_["zipCode"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
