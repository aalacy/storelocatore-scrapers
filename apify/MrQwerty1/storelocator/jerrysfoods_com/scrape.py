from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_token():
    data = {
        "app_key": "jerrys_foods",
        "referrer": "https://www.jerrysfoods.com/my-store/store-locator",
    }
    r = session.post("https://api.freshop.com/2/sessions/create", data=data)

    return r.json()["token"]


def fetch_data(sgw: SgWriter):
    api = f"https://api.freshop.com/1/stores?app_key=jerrys_foods&has_address=true&is_selectable=true&token={token}"
    r = session.get(api, headers=headers)
    js = r.json()["items"]

    for j in js:
        page_url = j.get("url")
        location_name = j.get("name")
        location_type = j.get("site_name")
        street_address = j.get("address_1")
        phone = j.get("phone_md")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = j.get("country").upper()
        city = j.get("city")
        store_number = j.get("store_number")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = "".join(j.get("hours_md"))
        if hours_of_operation.find("Kitchen") != -1:
            hours_of_operation = hours_of_operation.split("Kitchen")[0].strip()

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
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    token = get_token()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    locator_domain = "https://www.jerrysfoods.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
