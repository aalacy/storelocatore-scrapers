from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.post(
        "https://www.cafecoffeeday.com/ajax-getLocation", headers=headers, data=data
    )
    js = r.json()["locations"]

    for j in js:
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_name = j.get("name")
        street_address = j.get("address1")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("pincode")
        phone = j.get("phone")
        page_url = j.get("storeUrl")
        start = j.get("open_time")
        end = j.get("close_time")
        hours_of_operation = SgRecord.MISSING
        if start and end:
            hours_of_operation = f"{start}-{end}"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="IN",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.cafecoffeeday.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.cafecoffeeday.com/store-locator",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.cafecoffeeday.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    data = {
        "searchValue": "110005",
        "lat": "28.6556793",
        "lang": "77.1874601",
        "method": "searchByGoogleAutoFeildInput",
        "radius": "5000",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
