from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://marathonsportsbrand.locally.com/stores/conversion_data?has_data=true&company_id=108134&upc=&category=&show_links_in_list=true&parent_domain=&map_center_lat=42.38166944&map_center_lng=-71.12013117&map_distance_diag=3000"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    js = r.json()["markers"]

    for j in js:
        location_name = j.get("name") or ""
        slug = j.get("slug")
        if "Alley" in location_name:
            page_url = f"https://stores.runnersalley.com/{slug}"
        elif "Sound" in location_name:
            page_url = f"https://stores.soundrunner.com/{slug}"
        else:
            page_url = f"https://stores.marathonsports.com/{slug}"

        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("id")
        location_type = j.get("disclaimer")

        _tmp = []
        hours = j.get("display_dow").values()
        for h in hours:
            day = h.get("label")
            inter = h.get("bil_hrs")
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.marathonsports.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
