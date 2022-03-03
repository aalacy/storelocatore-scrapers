from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.cl"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json",
        "Accept-Language": "en",
        "Content-Language": "en",
        "Device-UUID": "6902c652-e717-4c56-8362-e8f334d6aca7",
        "Application": "39f9815013db3577160bb7891c853294",
        "Origin": "https://www.burgerking.cl",
        "Connection": "keep-alive",
        "Referer": "https://www.burgerking.cl/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    json_data = {
        "latitude": -32.485813,
        "longitude": -69.651575,
        "radius": 500000,
        "device_uuid": "rista@menu.app",
    }

    r = session.post(
        "https://api-lac.menu.app/api/directory/search", headers=headers, json=json_data
    )
    js = r.json()["data"]["venues"]
    for j in js:

        a = j.get("venue")
        page_url = "https://www.burgerking.cl/locales/"
        location_name = a.get("name") or "<MISSING>"
        types = a.get("order_types")
        tmp_type = []
        for t in types:
            typee = t.get("reference_type")
            tmp_type.append(typee)
        location_type = ", ".join(tmp_type)
        street_address = a.get("address") or "<MISSING>"
        state = "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "CL"
        city = a.get("city") or "<MISSING>"
        store_number = a.get("id") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        phone = a.get("phone") or "<MISSING>"
        hours = a.get("serving_times")
        tmp = []
        for h in hours:
            days = h.get("days")
            if len(days) == 7:
                days = "Monday to Sunday"
            opens = h.get("time_from")
            closes = h.get("time_to")
            line = f"{days} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = " ".join(tmp)

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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
