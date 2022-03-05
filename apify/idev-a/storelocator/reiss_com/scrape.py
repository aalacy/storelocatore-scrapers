from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.reiss.com"
base_url = "https://www.reiss.com/storelocator/data/stores"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["Stores"]
        for _ in locations:
            page_url = f"https://www.reiss.com/storelocator/{_['NA'].lower().replace(' ','')}/{_['BR']}?sv=list"
            hours = []
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            info = json.loads(sp1.find("script", type="application/ld+json").string)
            addr = info["address"]
            for hh in _.get("openingHoursSpecification", []):
                hours.append(f"{hh['dayOfWeek']}: {hh['opens']} - {hh['closes']}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["BR"],
                location_name=info["name"],
                street_address=addr["streetAddress"],
                city=addr["addressLocality"],
                state=addr.get("addressRegion"),
                zip_postal=addr.get("postalCode"),
                latitude=_["LT"],
                longitude=_["LN"],
                country_code=addr["addressCountry"],
                phone=info["telephone"],
                location_type=info["@type"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
