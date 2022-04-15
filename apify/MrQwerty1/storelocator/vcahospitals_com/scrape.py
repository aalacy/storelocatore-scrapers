from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://vcahospitals.com/fah-api/search-hospital"
    json_data = {
        "CurrentLat": 33.0218117,
        "CurrentLng": -97.12516989999999,
        "MinLatitude": -90,
        "MaxLatitude": 90,
        "MinLongitude": -180,
        "MaxLongitude": 180,
        "Radius": "5000",
        "SearchText": "75022",
        "HospitalType": "All Hospitals",
        "Country": "{70009942-4B02-4B03-96D0-FEC086AFB342}",
        "DataItemId": "{E591FBD6-4ECA-48DB-8A6B-69AF7D50CEFB}",
    }

    r = session.post(api, headers=headers, json=json_data)
    js = r.json()["result"]

    for j in js:
        location_name = j.get("Name")
        slug = j.get("Url") or ""
        page_url = f"https://vcahospitals.com{slug}"
        street_address = (
            f'{j.get("AddressLine1")} {j.get("AddressLine2") or ""}'.strip()
        )
        city = j.get("City")
        state = j.get("State")
        postal = j.get("Zipcode")

        phone = j.get("PhoneNumber") or ""
        if ":" in phone:
            phone = phone.split(":")[-1].strip()
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")

        _types = []
        types = j.get("HospitalTypes") or []
        for t in types:
            _types.append(t.get("DisplayName"))
        location_type = ", ".join(_types)
        store_number = j.get("branch_id")

        _tmp = []
        hours = j.get("Hours") or {}
        for day, inter in hours.items():
            _tmp.append(f"{day}: {inter}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            location_type=location_type,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://vcahospitals.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://vcahospitals.com/find-a-hospital/",
        "Origin": "https://vcahospitals.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_TYPE}
            )
        )
    ) as writer:
        fetch_data(writer)
