import datetime
import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    session = SgRequests()

    locator_domain = "https://www.greatvalu.com/"
    api_url = "https://api.freshop.com/1/stores?app_key=unfi_great_value&has_address=true&is_selectable=true&limit=100&token={}"
    d = datetime.datetime.now()
    unixtime = datetime.datetime.timestamp(d) * 1000
    frm = {
        "app_key": "unfi_great_value",
        "referrer": "https://www.greatvalu.com/",
        "utc": str(unixtime).split(".")[0],
    }
    r = session.post("https://api.freshop.com/2/sessions/create", data=frm).json()
    token = r["token"]

    r = session.get(api_url.format(token))
    js = json.loads(r.text)

    for j in js["items"]:

        page_url = j.get("url")
        location_name = j.get("name")
        street_address = j.get("address_1")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "USA"
        city = j.get("city")
        store_number = j.get("id")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = "".join(j.get("phone_md"))
        if phone.find("\n") != -1:
            phone = phone.split("\n")[0].strip()
        phone = phone.replace("Phone:", "").strip()
        hours_of_operation = "".join(j.get("hours_md")).replace("\n", " ").strip()

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
    locator_domain = "https://www.greatvalu.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
