from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://cdn.shopify.com/s/files/1/0568/4484/5206/t/2/assets/sca.storelocatordata.json"
    page_url = "https://www.planetbeauty.com/pages/store-locator"
    r = session.get(api)

    for j in r.json():
        location_name = j.get("name")
        street_address = j.get("address")
        phone = j.get("phone")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal")
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("priority")
        source = j.get("schedule") or "<html></html>"
        tree = html.fromstring(source)
        hours = tree.xpath("//text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.planetbeauty.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
