from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = (
            str(h.get("day"))
            .replace("1", "Mon")
            .replace("2", "Tue")
            .replace("3", "Wed")
            .replace("4", "Thu")
            .replace("5", "Fri")
            .replace("6", "Sat")
            .replace("0", "Sun")
        )
        opens = h.get("dineInOpen")
        closes = h.get("dineInClose")
        line = f"{day} {opens} - {closes}"
        if opens == closes:
            line = f"{day} Closed"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp)
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://wingsover.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json;charset=utf-8",
        "Client": "wingsover",
        "OS": "Web",
        "SessionId": "bc14705a-0f96-4dae-a2f6-d9d15bbb21c5",
        "Version": "2.59.9",
        "Origin": "https://order.wingsover.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    data = "{}"

    r = session.post(
        "https://patron.lunchbox.io/v0/locations", headers=headers, data=data
    )
    js = r.json()

    for j in js:
        a = j.get("address")
        page_url = "https://order.wingsover.com/"
        location_name = j.get("name")
        street_address = f"{a.get('street1')} {a.get('street2')}".strip()
        state = a.get("state")
        postal = a.get("zip")
        country_code = "US"
        city = a.get("city")
        latitude = a.get("geo").get("lat")
        longitude = a.get("geo").get("long")
        phone = j.get("phone").get("value")
        hours_of_operation = "<MISSING>"
        hours = j.get("hours") or "<MISSING>"
        if hours != "<MISSING>":
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
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
