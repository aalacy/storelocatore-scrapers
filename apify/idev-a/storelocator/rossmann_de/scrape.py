from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import json

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.rossmann.de"
base_url = "https://www.rossmann.de/de/filialen/assets/data/locations.json"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for key, _ in locations.items():
            page_url = f"{locator_domain}/de/filialen/{_['url']}"
            logger.info(page_url)
            ss = json.loads(
                bs(session.get(page_url, headers=_headers).text, "lxml")
                .find("script", type="application/ld+json")
                .string
            )
            location_type = ""
            if _["temporaryClosed"]:
                location_type = "temporary closed"
            hours = []
            for hh in _["groupedHours"]:
                times = []
                if hh["times"]:
                    for hr in hh["times"]:
                        times.append(f"{hr['openTime']} - {hr['closeTime']}")
                if not times:
                    times = ["closed"]
                hours.append(f"{hh['period']}: {', '.join(times)}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["storeCode"],
                location_name=_["name"],
                street_address=_["address"],
                city=_["locality"],
                state=_["region"],
                zip_postal=_["postalCode"],
                latitude=_["lat"],
                longitude=_["lng"],
                phone=ss["address"].get("telephone"),
                country_code="Germany",
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
