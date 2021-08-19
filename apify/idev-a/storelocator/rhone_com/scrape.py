from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.rhone.com"
page_url = "https://www.rhone.com/pages/find-retail-location"


def fetch_data():
    with SgRequests() as session:
        store_list = json.loads(
            session.get(
                "https://stockist.co/api/v1/u1742/locations/all.js?callback=_stockistAllStoresCallback"
            ).text.split("_stockistAllStoresCallback(")[1][:-2]
        )
        for _ in store_list:
            street_address = _["address_line_1"]
            if _["address_line_2"]:
                street_address += " " + _["address_line_2"]
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal_code"],
                locator_domain=locator_domain,
                country_code="US",
                latitude=_["latitude"],
                longitude=_["longitude"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
