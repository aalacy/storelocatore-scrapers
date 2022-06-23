import datetime
import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    session = SgRequests()

    locator_domain = "https://colemans.ca/"
    api_url = "https://api.freshop.com/1/stores?app_key=colemans&has_address=true&limit=-1&token={}"
    d = datetime.datetime.now()
    unixtime = datetime.datetime.timestamp(d) * 1000
    frm = {
        "app_key": "colemans",
        "referrer": "https://colemans.ca/",
        "utc": str(unixtime).split(".")[0],
    }
    r = session.post("https://api.freshop.com/2/sessions/create", data=frm).json()
    token = r["token"]

    r = session.get(api_url.format(token))
    js = json.loads(r.text)

    for j in js["items"]:

        street_address = f"{j.get('address_0')} {j.get('address_1')}".replace(
            "None", ""
        ).strip()
        city = j.get("city")
        postal = j.get("postal_code")
        state = j.get("state")
        country_code = "CA"
        store_number = j.get("store_number")
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        page_url = "https://shop.colemans.ca/my-store/store-locator"
        phone = j.get("phone_md")
        if str(phone).find("Curbside") != -1:
            phone = str(phone).split("Main:")[1].split("Curbside")[0].strip()
        hours_of_operation = (
            "".join(j.get("hours_md")).replace("Open", "").replace("\n", ", ").strip()
        )

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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
