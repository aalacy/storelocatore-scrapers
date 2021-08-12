from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = (
        "https://www.northcascadesbank.com/_/api/atms/47.8405882/-120.0164324/1000"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["atms"]:

        page_url = "https://www.northcascadesbank.com/locations"
        location_name = j.get("name")
        location_type = "ATM"
        street_address = "".join(j.get("address"))
        if street_address.find("\n") != -1:
            street_address = street_address.split("\n")[1].strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = "USA"
        city = j.get("city")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("long")

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
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.northcascadesbank.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
