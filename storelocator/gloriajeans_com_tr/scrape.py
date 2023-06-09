from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.gloriajeans.com.tr"
base_url = "https://www.gloriajeans.com.tr/subelerimiz"
json_url = "https://www.gloriajeans.com.tr/stores_json/{}"


def fetch_data():
    with SgRequests() as session:
        cities = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var cities =")[1]
            .split(";")[0]
        )
        for city in cities:
            logger.info(city[0])
            locations = session.get(json_url.format(city[1]), headers=_headers).json()
            for _ in locations:
                yield SgRecord(
                    page_url="https://www.gloriajeans.com.tr/subelerimiz",
                    location_name=_["title"],
                    street_address=_["street"],
                    city=_["city"],
                    zip_postal=_["zip"],
                    latitude=_["lat"],
                    longitude=_["lng"],
                    country_code="Turkey",
                    locator_domain=locator_domain,
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
