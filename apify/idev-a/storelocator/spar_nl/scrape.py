from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("spar")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.spar.nl"
base_url = "https://www.spar.nl/winkels/"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.c-store-list-panel__commands div.column")
        for _ in locations:
            page_url = locator_domain + _.a["href"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            ss = json.loads(sp1.find("script", type="application/ld+json").string)
            addr = ss["address"]
            hours = []
            for hh in ss["openingHoursSpecification"]:
                hours.append(f"{hh['dayOfWeek']}: {hh['opens']} - {hh['closes']}")
            yield SgRecord(
                page_url=page_url,
                location_name=ss["name"],
                street_address=addr["streetAddress"],
                city=addr["addressLocality"],
                zip_postal=addr["postalCode"],
                country_code="NL",
                phone=ss["telephone"],
                latitude=ss["geo"]["latitude"].replace(",", "."),
                longitude=ss["geo"]["longitude"].replace(",", "."),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(_.select_one("p.is-grey").stripped_strings),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
