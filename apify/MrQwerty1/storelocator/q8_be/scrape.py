from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    api = "https://www.q8.be/nl/get/stations.json"
    r = session.get(api, headers=headers)
    js = r.json()["Stations"]["Station"]

    for j in js:
        location_name = j.get("Name") or ""
        location_name = location_name.replace(">", " ")
        slug = j.get("NodeURL")
        page_url = f"https://www.q8.be{slug}"
        street_address = j.get("Address_line_1") or ""
        street_address = street_address.replace(">", "-")
        zc = j.get("Address_line_2") or ""
        postal = zc.split()[0]
        city = zc.replace(postal, "").strip()
        phone = j.get("Phone")
        latitude = j.get("XCoordinate") or ""
        longitude = j.get("YCoordinate") or ""
        if str(latitude) == "0":
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        store_number = j.get("StationId")
        country = j.get("Country")

        _tmp = []
        hours = j.get("OpeningHours") or {}
        for day, inter in hours.items():
            if inter:
                _tmp.append(f"{day}: {inter}")
            else:
                _tmp.append(f"{day}: Closed")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.q8.be/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
