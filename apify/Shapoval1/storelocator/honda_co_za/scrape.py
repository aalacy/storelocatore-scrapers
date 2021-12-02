from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda.co.za"
    api_url = "https://cms.honda.co.za/api/dealers?category=car&lng=22.937506&lat=-30.559482&key=18213a-23431-c0daj0-sa9da2"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json;charset=utf-8",
        "Accept-Language": "en",
        "Origin": "https://www.honda.co.za",
        "Connection": "keep-alive",
        "Referer": "https://www.honda.co.za/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]
    for j in js:

        page_url = "https://www.honda.co.za/cars/find-a-dealer"
        location_name = j.get("title") or "<MISSING>"
        a = j.get("address")
        street_address = a.get("street1") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        latitude = a.get("lat") or "<MISSING>"
        longitude = a.get("lng") or "<MISSING>"
        phone = j.get("contactUsNumber")
        hours_of_operation = f"Week {j.get('weekOfficeHours')} Weekend {j.get('weekendOfficeHours')}".replace(
            "Week None Weekend None", "<MISSING>"
        ).strip()

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
