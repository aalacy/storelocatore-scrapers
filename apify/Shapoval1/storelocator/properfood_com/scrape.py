from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("weekday")
        opens = h.get("open")
        closes = h.get("close")
        line = f"{day} {opens} - {closes}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://properfood.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Brandibble-Api-Key": "Bearer eyJhbGciOiJIUzI1NiIsImV4cCI6MjE2MzExMzg3MywiaWF0IjoxNTMyMzkzODczfQ.eyJlbWFpbCI6ImFsbGlzb25Ad2hpdGVzcGVjdHJlLmNvbSIsImRvbWFpbiI6Imh0dHA6Ly93d3cud2hpdGVzcGVjdHJlLmNvbSIsImFwaV91c2VyX2lkIjoxMCwibmFtZSI6IldoaXRlIFNwZWN0cmUifQ.AObdKkthOCsaSxHJFmsPDHdUpC-C2k6CsDEH2YAJ_PY",
        "Origin": "https://properfood.com",
        "Connection": "keep-alive",
        "Referer": "https://properfood.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    r = session.get(
        "https://www.brandibble.co/api/v1/brands/64/locations", headers=headers
    )
    js = r.json()["data"]
    for j in js:
        page_url = "https://properfood.com/locations/"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street_address") or "<MISSING>"
        state = j.get("state_code") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        has_pickup = j.get("has_pickup")
        if not has_pickup:
            continue
        store_number = j.get("location_id") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        hours = j.get("hours_pickup") or "<MISSING>"
        hours_of_operation = get_hours(hours)

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
