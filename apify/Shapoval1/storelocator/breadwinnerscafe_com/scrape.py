from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.breadwinnerscafe.com/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.breadwinnerscafe.com/",
        "content-type": "application/json",
        "Origin": "https://www.breadwinnerscafe.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = '{"operationName":"restaurantWithLocations","variables":{"restaurantId":10634},"extensions":{"operationId":"PopmenuClient/94a9b149c729821816fee7d97a05ecac"}}'

    r = session.post(
        "https://www.breadwinnerscafe.com/graphql", headers=headers, data=data
    )
    js = r.json()

    for j in js["data"]["restaurant"]["locations"]:

        slug = j.get("slug")
        page_url = f"https://www.breadwinnerscafe.com/{slug}"
        location_name = j.get("name")
        street_address = j.get("streetAddress")
        state = j.get("state")
        postal = j.get("postalCode")
        country_code = "US"
        city = j.get("city")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        hours_of_operation = " ".join(j.get("schemaHours"))
        ad = j.get("fullAddress")

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
