import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    page_url = "https://cefcostores.com/store-locator/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@id='map_data']/text()"))
    js = json.loads(text)

    for j in js:
        store_number = j.get("site") or ""
        location_name = f"CEFCO #{store_number}"
        store_number = store_number.split()[0]
        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=j.get("address"),
            city=j.get("city"),
            state=j.get("state"),
            zip_postal=j.get("zip"),
            country_code="US",
            store_number=store_number,
            latitude=j.get("latitude"),
            longitude=j.get("longitude"),
            locator_domain=locator_domain,
            hours_of_operation=j.get("hours"),
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://cefcostores.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
