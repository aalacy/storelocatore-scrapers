from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.johnsoncleaners.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.johnsoncleaners.com",
        "Connection": "keep-alive",
        "Referer": "https://www.johnsoncleaners.com/branch/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = {
        "search2": " ",
        "type": "5,1",
        "address": "UK United Kingdom",
        "start": "700",
    }

    r = session.post(
        "https://www.johnsoncleaners.com/storefinder/locator/get/55.378051/-3.435973/1",
        headers=headers,
        data=data,
    )
    js = r.json()["locations"]
    for j in js:

        page_url = f"https://www.johnsoncleaners.com/branch/{j.get('url')}"
        location_name = j.get("name")
        location_type = "Johnsons Cleaners"
        street_address = j.get("street1")
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country")
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = f"Monday {j.get('opening_1')} Tuesday {j.get('opening_2')} Wednesday {j.get('opening_3')} Thursday {j.get('opening_4')} Friday {j.get('opening_5')} Saturday {j.get('opening_6')} Sunday {j.get('opening_7')}"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.LATITUDE}))) as writer:
        fetch_data(writer)
