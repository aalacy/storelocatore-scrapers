from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.diamondparking.com"
base_url = "https://www.diamondparking.com/wp-content/plugins/diamond-parking/assets/data.json?ver=5.8.1"


def fetch_data():
    with SgRequests(verify_ssl=False) as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var $parkings =")[1]
            .strip()[:-1]
        )["locations"]
        for _ in locations:
            location_type = ", ".join(_["terms"])
            yield SgRecord(
                page_url="https://www.diamondparking.com/find-parking/",
                store_number=_["post_id"],
                location_name=_["post_title"].replace("&#8211;", "-"),
                street_address=_["address_place"],
                city=_["city_place"],
                state=_["state_place"],
                zip_postal=_["postalcode_place"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                location_type=location_type,
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
