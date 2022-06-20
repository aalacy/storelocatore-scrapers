from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.maxsrestaurantna.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.maxsrestaurantna.com/california",
        "Origin": "https://www.maxsrestaurantna.com",
        "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    json_data = {
        "operationName": "restaurantWithLocations",
        "variables": {
            "restaurantId": 5466,
        },
        "extensions": {
            "operationId": "PopmenuClient/4d4c3b13b2fd299b79e97dc193f1c22e",
        },
    }

    r = session.post(
        "https://www.maxsrestaurantna.com/graphql", headers=headers, json=json_data
    )
    js = r.json()["data"]["restaurant"]["locations"]
    for j in js:

        slug = j.get("slug")
        page_url = f"https://www.maxsrestaurantna.com/{slug}"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("streetAddress") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours = j.get("schemaHours")
        hours_of_operation = "<MISSING>"
        if hours:
            hours_of_operation = " ".join(hours)

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
