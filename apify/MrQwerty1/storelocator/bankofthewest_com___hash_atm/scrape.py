from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://www.bankofthewest.com/api/branches/GetByDistanceMobile"
    r = session.post(api, headers=headers, data=data)
    js = r.json()

    for j in js:
        page_url = j.get("HomepageUrl")
        location_name = f'Bank of West {j.get("Name")}'.strip()
        street_address = j.get("Address")
        city = j.get("City")
        state = j.get("State")
        postal = j.get("Zipcode")
        phone = j.get("PhoneNumber")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        hours_of_operation = j.get("WeekdayHours")
        location_type = j.get("Type")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            location_type=location_type,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://bankofthewest.com/#atm"
    headers = {"Content-Type": "application/json"}
    data = '{"lat":"41.1399814","lon":"-104.8202462","rad":100000,"btype":false,"mlofficer":false,"atm":true}'
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_TYPE}
            )
        )
    ) as writer:
        fetch_data(writer)
