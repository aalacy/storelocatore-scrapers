from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude=47.0818269&longitude=2.4039338&radius=2000"
    r = session.get(api, cookies=cookies)
    js = r.json()["locationDetails"]

    for j in js:
        location_name = j.get("displayAddress")
        street_address = j.get("address")
        city = j.get("city")
        postal = j.get("zip")
        country_code = j.get("countryCode")
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        hours = j.get("hours") or []
        for h in hours:
            day = h.get("day")
            start = h.get("open")
            end = h.get("close")
            if not start:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    cookies = {
        "WC_ACTIVEPOINTER": "-2%2C13801",
        "WC_USERACTIVITY_-1002": "-1002%2C13801%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C925451795%2CMuWFf7SnaPuH5lqDFeG%2FIK%2B9Qk92dpMYE9OAR4MIYUTjblgvaxnYFX2TlOZL1gv6%2FzmRfsUIFxUiTTTeCwMOI%2BTBNRLiGpEKVK6C0JfuYh9wZwHqXxDFqr%2FRGQmv3Uu%2FV5OzRuPPJ%2B9IxZxmoj7akcEgYSGbrZ9gUS1EkB6oTJqgcDfrnww0krSeTmwg7%2FgyBet4IRpctZ9sz0vDdmkVWr2Pzzb13nguZxUET2DyNpCKXo5VeY8e%2FaJ1cVqxacxU",
    }
    locator_domain = "https://www.sunglasshut.com/"
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.HOURS_OF_OPERATION}
            )
        )
    ) as writer:
        fetch_data(writer)
