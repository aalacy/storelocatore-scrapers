from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("day_name")
        opens = h.get("open_time")
        closes = h.get("end_time")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://maggianos.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://maggianos.com/",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    r = session.get("https://maggianos.com/api//restaurant-data/", headers=headers)
    js = r.json()
    for j in js:
        a = j.get("properties").get("slug")
        url_slug = j.get("properties").get("urlSlug") or "<MISSING>"
        location_name = j.get("properties").get("business_name") or "<MISSING>"
        street_address = (
            f"{a.get('address_line_1')} {a.get('address_line_2') or ''}".strip()
        )
        state = a.get("state")
        postal = a.get("postal_code")
        country_code = "US"
        city = a.get("city")
        page_url = "https://maggianos.com/locations/"
        if url_slug != "<MISSING>":
            page_url = f"https://maggianos.com/locations/{state}/{city}/{url_slug}"
        latitude = j.get("geometry").get("coordinates").get("latitude") or "<MISSING>"
        longitude = j.get("geometry").get("coordinates").get("longitude") or "<MISSING>"
        phone = j.get("properties").get("primary_phone") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("properties").get("store_hours") or "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = get_hours(hours)
        raw = j.get("properties").get("full_address")

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
