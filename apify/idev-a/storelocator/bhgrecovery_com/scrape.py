from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("bhgrecovery")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://bhgrecovery.com/"
    base_url = "https://bhgrecovery.com/locations/#"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.container section article")
        logger.info(f"{len(links)} found")
        for link in links:
            page_url = link.h4.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            addr = list(sp1.select_one("div.location-info p.font-15").stripped_strings)
            ss = json.loads(
                sp1.find("script", type="application/ld+json").string.strip()
            )
            _ss = ss["subOrganization"]
            hours = []
            for hh in _ss["openingHoursSpecification"]:
                day = ",".join(hh["dayOfWeek"])
                if type(hh["dayOfWeek"]) != list:
                    day = hh["dayOfWeek"]
                hours.append(f"{day}: {hh['opens']}-{hh['closes']}")
            yield SgRecord(
                page_url=page_url,
                location_name=_ss["name"].replace("&#8211;", "-").replace("–", "-"),
                street_address=" ".join(addr[:-1]),
                city=_ss["address"]["addressLocality"],
                state=_ss["address"]["addressRegion"],
                zip_postal=_ss["address"]["postalCode"],
                country_code="US",
                phone=_ss["telephone"],
                locator_domain=locator_domain,
                latitude=_ss["geo"]["latitude"],
                longitude=_ss["geo"]["longitude"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
