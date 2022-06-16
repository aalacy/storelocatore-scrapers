from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("carrefour")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://winkels.carrefour.be"
base_url = "https://winkels.carrefour.be/api/v3/locations"
hr_obj = {
    "1": "Monday",
    "2": "Tuesday",
    "3": "Wednesday",
    "4": "Thursday",
    "5": "Friday",
    "6": "Saturday",
    "7": "Sunday",
}


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = _["address"]
            hours = []
            if _["status"] != "OPEN":
                hours = [_["status"]]
            for hh in _["businessHours"]:
                day = hr_obj.get(str(hh["startDay"]))
                hours.append(f"{day}: {hh['openTimeFormat']} - {hh['closeTimeFormat']}")
            page_url = f"https://winkels.carrefour.be/nl/s/carrefour/{_['slug']}/{_['externalId']}"
            logger.info(page_url)
            phone = json.loads(
                bs(session.get(page_url, headers=_headers).text, "lxml")
                .find("script", type="application/ld+json")
                .string
            )["telephone"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["externalId"],
                location_name=_["name"],
                street_address=addr["street"],
                city=addr["locality"],
                zip_postal=addr["zipCode"],
                latitude=addr["latitude"],
                longitude=addr["longitude"],
                country_code=addr["country"],
                phone=phone,
                locator_domain=locator_domain,
                location_type=_["brandSlug"],
                hours_of_operation="; ".join(hours),
                raw_address=addr["fullAddress"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
