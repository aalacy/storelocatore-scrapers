from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("allstate")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://agents.allstate.ca"
base_url = "https://agents.allstate.ca/fr_ca/search.html"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        links = soup.select("div.bottom-link-list__list div.bottom-link a")
        logger.info(f"{len(links)} found")
        for link in links:
            state_url = locator_domain + link["href"]
            cities = bs(session.get(state_url, headers=_headers).text, "lxml").select(
                "div.bottom-col-list div.bottom-col-list__letter-group__links__link a"
            )
            logger.info(f"[{len(cities)}] {link['href']}")
            for city in cities:
                loc_url = locator_domain + city["href"]
                locations = bs(
                    session.get(loc_url, headers=_headers).text, "lxml"
                ).select("div.agent-card h3 a")
                logger.info(f"[{city['href']}] {len(locations)}")
                for _ in locations:
                    page_url = locator_domain + _["href"]
                    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
                    ss = json.loads(
                        f'[{sp1.find("script", type="application/ld+json").string}]'
                    )
                    yield SgRecord(
                        page_url=page_url,
                        location_name=sp1.select_one("h1.agency-name").text.strip(),
                        street_address=ss[0]["address"]["streetAddress"],
                        city=ss[0]["address"]["addressLocality"],
                        state=ss[0]["address"]["addressRegion"],
                        zip_postal=ss[0]["address"]["postalCode"],
                        country_code="CA",
                        phone=ss[0]["telephone"],
                        locator_domain=locator_domain,
                        latitude=ss[1]["latitude"],
                        longitude=ss[1]["longitude"],
                        location_type=ss[0]["@type"],
                        hours_of_operation="; ".join(ss[0]["openingHours"]).replace(
                            "–", "-"
                        ),
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
