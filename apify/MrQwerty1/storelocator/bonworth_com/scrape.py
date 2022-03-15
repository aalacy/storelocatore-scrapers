from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://cdn.shopify.com/s/files/1/0316/1577/8951/t/5/assets/sca.storelocatordata.json"

    r = session.get(api, headers=headers)

    for j in r.json():
        location_name = j.get("name")
        street_address = j.get("address")
        city = j.get("city") or ""
        if "," in city:
            city = city.split(",")[0].strip()
        state = j.get("state")
        postal = j.get("postal")
        country_code = "US"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = j.get("schedule")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://bonworth.com/"
    page_url = "https://bonworth.com/pages/store-locator"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
