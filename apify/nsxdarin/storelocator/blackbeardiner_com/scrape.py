import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://blackbeardiner.com"
    api_url = "https://passport.blackbeardiner.com/api/locations?callback=callback_for_jsonp&_=1633470148738"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js_block = r.text.split("callback_for_jsonp(")[1].split(");")[0].strip()
    js = json.loads(js_block)
    for j in js:

        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('street_address')} {j.get('street_address_2')}".strip()
        )
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = "".join(j.get("city")) or "<MISSING>"
        city_slug = city.lower().replace(" ", "-").strip()
        page_url = f"https://blackbeardiner.com/location/{city_slug}/"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = (
            "".join(j.get("hours_of_operation")).replace("\r\n", " ").strip()
            or "<MISSING>"
        )
        if hours_of_operation.find("<") != -1:
            hours_of_operation = hours_of_operation.split("<")[0].strip()

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
