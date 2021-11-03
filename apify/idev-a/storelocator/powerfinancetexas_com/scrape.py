from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("powerfinancetexas")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def fetch_data():
    locator_domain = "https://www.powerfinancetexas.com"
    base_url = "https://www.powerfinancetexas.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = (
            soup.find("a", string=re.compile(r"Locations"))
            .find_next_sibling("ul")
            .select("a")
        )
        for link in links:
            logger.info(link["href"])
            res = session.get(link["href"], headers=_headers)
            if res.status_code != 200:
                logger.info("- 404 -")
                continue
            sp1 = bs(res.text, "lxml")
            _script = sp1.find_all("script", type="application/ld+json")
            if len(_script) < 2:
                logger.info("-- 404 --")
                continue
            _ = json.loads(_script[-1].string.strip())
            hours = []
            for hh in _["openingHoursSpecification"]:
                days = hh["dayOfWeek"]
                if type(days) != list:
                    days = [days]
                hours.append(f"{','.join(days)}: {hh['opens']}-{hh['closes']}")
            coord = (
                sp1.iframe["src"]
                .split("!2d")[1]
                .split("!3m")[0]
                .split("!2m")[0]
                .split("!3d")
            )
            yield SgRecord(
                page_url=link["href"],
                location_name=sp1.h1.text.strip(),
                street_address=_["address"]["streetAddress"],
                city=_["address"]["addressLocality"],
                state=_["address"]["addressRegion"],
                zip_postal=_["address"]["postalCode"],
                phone=_["telephone"],
                latitude=coord[1],
                longitude=coord[0],
                country_code="US",
                locator_domain=locator_domain,
                hours_of_operation=_valid("; ".join(hours)),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
