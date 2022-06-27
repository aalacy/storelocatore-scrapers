import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://marketingsl.tjx.com/storelocator/GetSearchResultsByRegion/?chain=20&region=40"

    r = session.get(api)
    text = r.text.replace("<p>", "").replace("</p>", "")
    js = json.loads(text)["Stores"]

    for j in js:
        location_name = j.get("Name") or ""
        slug = location_name.replace(" ", "-").replace(",-", ",")
        page_url = f"https://www.tkmaxx.com.au/store-locator/{slug}"
        street_address = j.get("Address")
        city = j.get("City")
        state = j.get("State")
        postal = j.get("Zip")
        if state in postal:
            postal = postal.replace(state, "").strip()
        phone = j.get("Phone")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        store_number = j.get("StoreID")

        text = j.get("Hours") or "<html>"
        root = html.fromstring(text)
        hours = root.xpath("//text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours)
        if "stay" in hours_of_operation.lower() or not hours_of_operation:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="AU",
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.tkmaxx.com.au/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
