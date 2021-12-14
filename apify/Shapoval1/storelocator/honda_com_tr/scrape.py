from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.com.tr/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    data = {"vehicle_type_id": "1"}

    r = session.post(
        "https://honda.com.tr/backend/web/static/getDealers", headers=headers, data=data
    )
    js = r.json()["success"]["dealers"]
    for j in js:

        page_url = "https://honda.com.tr/otomobil/iletisim"
        location_name = j.get("title")
        street_address = j.get("address")
        state = j.get("county").get("name")
        postal = "<MISSING>"
        country_code = "TR"
        city = j.get("city").get("name")
        coords = j.get("coords")
        a = eval(coords)
        latitude = a.get("lat")
        longitude = a.get("lng")
        phone = j.get("phone")

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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
