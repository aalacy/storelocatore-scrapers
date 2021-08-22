from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://api.freshop.com/1/stores?app_key=king_food_saver&has_address=true&limit=-1&token=67f1de4e07058a58312308e9ed6a1b84"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["items"]:

        page_url = j.get("url")
        location_name = j.get("name")
        location_type = j.get("site_name")
        street_address = j.get("address_1")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "USA"
        city = j.get("city")
        store_number = j.get("store_number")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = "".join(j.get("phone_md"))
        if phone.find("\n") != -1:
            phone = phone.split("\n")[0].replace(")4", ") 4").strip()
        hours_of_operation = "".join(j.get("hours_md")).replace("\n", " ").strip()
        if hours_of_operation.find("Market") != -1:
            hours_of_operation = hours_of_operation.split("Market")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
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
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.kingfoodsaver.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
