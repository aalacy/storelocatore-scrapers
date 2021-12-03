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
        "WC_USERACTIVITY_-1002": "-1002%2C13801%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1892784604%2CeXD7UsDc%2BzQb4ENrom1bsP%2FGymq9qfjsVGY58DlH4syXzSfDvhHXUpdvmmHABnc54Xw5JqBCOA1sHoOycDKiUUUGZIwySicq8X3cfdSL3jmDkRg1mLDX2W%2F%2Bt3GYJAe%2F2ShBTKyNUiXSJoLZpcO2nG4wfEoGypgqm4Wv6E0U4UL8nLCF42JRfwBWkCEnVWWWNkYYukZuZnDckIhgYj3CL0%2FhUPD7H5TGam561IiQgtWF9psnBh3%2FGtvk3HUVm57D",
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
