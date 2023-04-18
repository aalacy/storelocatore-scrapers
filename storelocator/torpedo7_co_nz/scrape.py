from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("torpedo7")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.torpedo7.co.nz"
base_url = "https://www.torpedo7.co.nz/store-locator"


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.storeItem"
        )
        for link in locations:
            page_url = locator_domain + link.a["href"]
            logger.info(page_url)
            ss = json.loads(
                bs(session.get(page_url, headers=_headers).text, "lxml")
                .find("script", type="application/ld+json")
                .string
            )
            addr = ss["address"]
            hours = []
            for hh in ss.get("openingHoursSpecification", []):
                hours.append(f"{hh['dayOfWeek']}: {hh['opens']} - {hh['closes']}")
            city = addr["addressRegion"]
            yield SgRecord(
                page_url=page_url,
                location_name=ss["name"],
                street_address=addr["streetAddress"],
                city=city,
                zip_postal=addr["postalCode"],
                latitude=ss["geo"]["latitude"],
                longitude=ss["geo"]["longitude"],
                country_code="NZ",
                phone=ss["telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
