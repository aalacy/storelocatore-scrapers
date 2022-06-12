from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json
import re

logger = SgLogSetup().get_logger("hustlerhollywood")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://hustlerhollywood.com"
base_url = "https://hustlerhollywood.com/pages/our-stores"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("article.store-item")
        for _ in locations:
            if not _.select_one("div.store-item__link a"):
                continue
            page_url = locator_domain + _.select_one("div.store-item__link a")["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            ss = json.loads(sp1.find("script", string=re.compile('"geo"')).string)
            hours = []
            if _.select("div.store-item__hours"):
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in _.select("div.hours-sort-container")[0].select(
                        "div.hours-row"
                    )
                ]
            yield SgRecord(
                page_url=page_url,
                location_name=ss["name"],
                street_address=ss["address"]["streetAddress"],
                city=ss["address"]["addressLocality"],
                state=ss["address"]["addressRegion"],
                zip_postal=ss["address"]["postalCode"],
                country_code=ss["address"]["addressCountry"],
                phone=ss["telephone"],
                latitude=ss["geo"]["latitude"],
                longitude=ss["geo"]["longitude"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
