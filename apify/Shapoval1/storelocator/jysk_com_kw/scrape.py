from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jysk.com.kw/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://jysk.com.kw",
        "Connection": "keep-alive",
        "Referer": "https://jysk.com.kw/stores",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    data = {
        "lat": "0",
        "lng": "0",
        "radius": "0",
        "product": "0",
        "category": "0",
        "sortByDistance": "1",
    }

    r = session.post(
        "https://jysk.com.kw/amlocator/index/ajax/", headers=headers, data=data
    )
    js = r.json()["items"]
    for j in js:

        page_url = "https://jysk.com.kw/stores"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = "".join(j.get("zip")) or "<MISSING>"
        if postal.count("0") > 3:
            postal = "<MISSING>"
        country_code = "KW"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        h = eval(j.get("schedule_string"))
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        tmp = []
        for d in days:
            day = d
            opens = (
                h.get(f"{d}").get("from").get("hours")
                + "."
                + h.get(f"{d}").get("from").get("minutes")
            )
            closes = (
                h.get(f"{d}").get("to").get("hours")
                + "."
                + h.get(f"{d}").get("to").get("minutes")
            )
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
