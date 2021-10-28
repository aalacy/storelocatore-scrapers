from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.sunglasshut.com/AjaxSGHFindPhysicalStoreLocations?latitude=48.83&longitude=2.12&radius=2000"
    r = session.get(api, cookies=cookies)
    js = r.json()["locationDetails"]

    for j in js:
        s = j.get("shippingDetails") or {}
        location_name = j.get("displayAddress")
        street_address = j.get("address")
        city = j.get("city")
        postal = s.get("zipCode") or j.get("zip")
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
        "WC_USERACTIVITY_1454163400": "1454163400%2C13801%2Cnull%2Cnull%2C1635419463778%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C925451795%2CSP1YIlJUeWHtUKhDq5aD2k1OkrZLCvHeIf7usnxyPviSFS%2BMEYL3om%2FtusJhvGOjMZL6hg4yKYxGxgGgcCWgdzXtC11S3n53rBLvGV5kh6IJzHTv8oB7qg16A9Q44pRkWpgNyQqH3HU0AjilFr8OWT2RLQzqYJ8T9QxqKf2x%2BWeGlsvWvT3FkVOvaIEr6LgzxdYSeTp1BzpEElwvJQWiyH5xnIM3m%2BuiMaY8SPw240qxiyaA546dC5vN4SFEzjbqwEM%2BgbqJmSXNcRgZvjq7%2Bw%3D%3D",
        "WC_AUTHENTICATION_1454163400": "1454163400%2CVLgN0C5Nv%2FaK4J8B%2B%2Be3yYmE8gAmItbLgWe9Wl4HPbQ%3D",
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
