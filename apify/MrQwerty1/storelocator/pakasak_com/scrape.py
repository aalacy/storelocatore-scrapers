import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.pakasak.com/e107_plugins/stores/store_locator.php"
    r = session.get(api)

    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var markersOnMap =')]/text()")
    )
    text = text.split("var markersOnMap =")[1].split("];")[0] + "]"
    js = json5.loads(text)

    for j in js:
        try:
            geo = j["LatLng"][0]
        except:
            geo = dict()

        location_name = j.get("placeName") or ""
        if "Change" in location_name:
            continue

        street_address = (
            f"{j.get('storeStreet1')} {j.get('storeStreet2') or ''}".strip()
        )
        city = j.get("storeCity")
        state = j.get("storeState")
        postal = j.get("storeZip")
        country_code = "US"
        phone = j.get("storeCity")
        latitude = geo.get("lat")
        longitude = geo.get("lng")
        store_number = j.get("storeId")
        page_url = (
            f"https://www.pakasak.com/e107_plugins/stores/view_store.php?{store_number}"
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.pakasak.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
