from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson as json
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("cpb")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.replace("&#39;", "&")
        .replace("&amp;", "&")
        .replace("&a", "'a")
        .replace("&s", "'s")
        .replace("–", "-")
        .replace("’", "'")
    )


def _removeComma(val):
    if val.endswith(","):
        val = val[:-1]
    return val


def fetch_data():
    locator_domain = "https://www.cpb.bank"
    base_url = "https://www.cpb.bank/locations"
    with SgRequests() as session:
        res = session.get(base_url, headers=_headers).text
        locations = []
        for loc in res.split("node =")[1:]:
            locations.append(
                json.loads(
                    loc.split("locations.push")[0]
                    .strip()[:-1]
                    .replace("servicesList", '""')
                )
            )
        for _ in locations:
            page_url = locator_domain + _["pageLink"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            street_address = _["addr1"]
            if _["addr2"]:
                street_address += " " + _["addr2"]
            street_address = _removeComma(street_address).split(",")[0].strip()
            hours = []
            hours.append(f"Mon-Thu: {_['monHours']}")
            hours.append(f"Fri: {_['friHours']}")
            hours.append(f"Sat: {_['satHours']}")
            hours.append(f"Sun: {_['sunHours']}")
            yield SgRecord(
                page_url=page_url,
                location_name=_valid(_["name"]),
                street_address=_valid(street_address),
                city=_removeComma(_["city"]),
                state=_["state"],
                zip_postal=_["zipcode"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=sp1.find("h3", string=re.compile(r"Phone"))
                .find_next_sibling()
                .text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
