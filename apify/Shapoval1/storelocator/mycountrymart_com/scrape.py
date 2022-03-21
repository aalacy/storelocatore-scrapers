import datetime
import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    session = SgRequests()

    locator_domain = "https://www.mycountrymart.com"
    api_url = "https://api.freshop.com/1/stores?app_key=mycountrymart&has_address=true&is_selectable=true&limit=100&token={}"
    d = datetime.datetime.now()
    unixtime = datetime.datetime.timestamp(d) * 1000
    frm = {
        "app_key": "mycountrymart",
        "referrer": "https://www.mycountrymart.com/",
        "utc": str(unixtime).split(".")[0],
    }
    r = session.post("https://api.freshop.com/2/sessions/create", data=frm).json()
    token = r["token"]

    r = session.get(api_url.format(token))
    js = json.loads(r.text)

    for j in js["items"]:

        street_address = f"{j.get('address_1')} {j.get('address_2')}".replace(
            "None", ""
        ).strip()
        city = j.get("city")
        postal = j.get("postal_code")
        state = j.get("state")
        country_code = "US"
        store_number = j.get("store_number")
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        page_url = j.get("url")
        phone = j.get("phone_md")
        hours_of_operation = (
            "".join(j.get("hours_md")).replace("Open", "").replace("\n", ", ").strip()
        )
        if hours_of_operation.find("First") != -1:
            hours_of_operation = hours_of_operation.split("First")[0].strip()

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.mycountrymart.com"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
