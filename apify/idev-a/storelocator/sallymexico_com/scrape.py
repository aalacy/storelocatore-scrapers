from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

locator_domain = "https://www.sallymexico.com"
base_url = "https://www.sallymexico.com/stores"
json_url = "/api/dataentities/WH/scroll"
asset_url = "sallybeautymx.vtexassets.com/_v/public/assets/v1/published/bundle/public/react/asset.min.js\?v=1\&files=vtex.sticky-layout"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url, timeout=15)
        ra = driver.wait_for_request(asset_url, timeout=15)
        _hr = (
            ra.response.body.decode()
            .split('"description-store-horario"},')[1]
            .split("),t.Rappi")[0]
            .split(',i.a.createElement("br",null),')
        )
        hours = []
        hours.append(_hr[0].strip()[1:-1].strip())
        hours.append(_hr[1].strip()[1:-1].strip())
        locations = json.loads(rr.response.body)
        for _ in locations:
            yield SgRecord(
                page_url=base_url,
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["address"].replace("\n", " "),
                city=_["city"],
                state=_["stateCode"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="Mexico",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
