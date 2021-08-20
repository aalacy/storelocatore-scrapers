from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("cinnaholic")

_header1 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def fetch_data():
    names = []
    with SgRequests() as session:
        locator_domain = "https://cinnaholic.com"
        base_url = "https://locations.cinnaholic.com/locations-list/"
        soup = bs(session.get(base_url, headers=_header1).text, "lxml")
        states = soup.select("div.content ul li a")
        for state in states:
            soup1 = bs(
                session.get(
                    f'https://locations.cinnaholic.com{state["href"]}', headers=_header1
                ).text,
                "lxml",
            )
            cities = soup1.select("div.content ul li a")
            for city in cities:
                soup3 = bs(
                    session.get(
                        f'https://locations.cinnaholic.com{city["href"]}',
                        headers=_header1,
                    ).text,
                    "lxml",
                )
                details = soup3.select("div.content ul li a")
                for detail in details:
                    page_url = detail["href"]
                    logger.info(f"[{state.text}] [{city.text}] [{page_url}]")
                    soup4 = bs(session.get(page_url, headers=_header1).text, "lxml")
                    _ = json.loads(
                        soup4.find_all("script", type="application/ld+json")[-1].string
                    )
                    if _["name"] not in names:
                        names.append(_["name"])
                    else:
                        continue

                    hours = []
                    if soup4.select("div.hours-box .day-row"):
                        hours = [
                            ": ".join(hh.stripped_strings)
                            for hh in soup4.select("div.hours-box .day-row")
                        ]
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_["name"],
                        street_address=_["address"]["streetAddress"],
                        city=_["address"]["addressLocality"],
                        state=_["address"]["addressRegion"],
                        zip_postal=_["address"]["postalCode"],
                        country_code="US",
                        phone=_.get("telephone"),
                        locator_domain=locator_domain,
                        latitude=_["geo"]["latitude"],
                        longitude=_["geo"]["longitude"],
                        location_type=_["@type"],
                        hours_of_operation="; ".join(hours).replace("–", "-"),
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
