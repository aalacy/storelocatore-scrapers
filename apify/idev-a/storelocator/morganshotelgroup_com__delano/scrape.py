from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("sbe")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.sbe.com"
base_url = "https://www.sbe.com/properties.json"


def _d(page_url, session):
    sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
    ss = json.loads(sp1.find_all("script", type="application/ld+json")[1].string)
    coord = json.loads(
        sp1.find(
            "script", attrs={"data-drupal-selector": "drupal-settings-json"}
        ).string
    )["verb_directions"]["location"]
    return SgRecord(
        page_url=page_url,
        location_name=ss["name"],
        street_address=ss["address"]["streetAddress"],
        city=ss["address"].get("addressLocality"),
        state=ss["address"].get("addressRegion"),
        zip_postal=ss["address"].get("postalCode"),
        country_code=ss["address"]["addressCountry"],
        latitude=coord["lat"],
        longitude=coord["lng"],
        phone=ss.get("telephone"),
        locator_domain=locator_domain,
    )


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["properties"]
        for _ in locations:
            if not _["marketingLink"]:
                continue
            page_url = locator_domain + _["marketingLink"]
            logger.info(page_url)
            yield _d(page_url, session)
        links = bs(
            session.get("https://www.sbe.com/hotels/delano", headers=_headers).text,
            "lxml",
        ).select("div.cards__row div.card--properties div.card__text")
        for link in links:
            page_url = locator_domain + link.a["href"]
            if "Coming Soon" in link.text:
                continue
            logger.info(page_url)
            yield _d(page_url, session)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
