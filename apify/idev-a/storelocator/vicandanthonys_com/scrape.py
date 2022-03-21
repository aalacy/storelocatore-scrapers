from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("vicandanthonys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.vicandanthonys.com"
    base_url = "https://www.vicandanthonys.com/locations/"
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("locations:")[1]
            .split("apiKey:")[0]
            .strip()[:-1]
        )
        logger.info(f"{len(locations)} found")
        for _ in locations:
            page_url = locator_domain + _["url"]
            hours = []
            for hh in bs(_["hours"], "lxml").stripped_strings:
                if (
                    "Happy" in hh
                    or "Pick" in hh
                    or "Bar" in hh
                    or "Closing" in "hh"
                    or "Please" in hh
                ):
                    break
                hours.append(hh)
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["street"],
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                country_code="US",
                phone=_["phone_number"],
                locator_domain=locator_domain,
                latitude=_["lat"],
                longitude=_["lng"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
