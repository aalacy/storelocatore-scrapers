from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude=50.5644045&longitude=9.5794967&radius=2000"
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
        "WC_ACTIVEPOINTER": "-3%2C14351",
        "WC_USERACTIVITY_-1002": "-1002%2C14351%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C925451795%2CnsuAATuCz8TV9jIEToBzMNsbQnHEEKqM97uF3kTctq5k1GX5NcHKGtQtEjoj1VeALlTTW9BRtxaOrVvmiClpJnSR8JMxAwofH%2BJpRhKEQMXMDo9NAeYAaW6XS8jrUhe1RMVEd9IueSUaaDtlBhNMddEqfQ39EUwYE77NaGHhEO344GvWo8txsqXoQGPtsIBqhxWo3Xx%2BfmYIfbOU%2FX%2BHmxvqv7fjCYXRkAO89x6kdFeZ%2BjcST6LMBlfzK1sqdrlr",
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
