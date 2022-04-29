from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://burgerking.fi/"
    api_url = "https://burgerking.fi/wp-json/v2/restaurants"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://burgerking.fi/etsi-ravintola/"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        country_code = "FI"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("location").get("lat") or "<MISSING>"
        longitude = j.get("location").get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
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
            times = j.get("visiting_hours").get(f"{d}") or "<MISSING>"
            line = f"{day} {times}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if hours_of_operation.count("<MISSING>") != 7:
            hours_of_operation = hours_of_operation.replace("<MISSING>", "Closed")
        if hours_of_operation.count("<MISSING>") == 7:
            hours_of_operation = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
