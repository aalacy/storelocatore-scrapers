from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bankofcolorado.com"
    api_url = "https://www.bankofcolorado.com/locator/json?lat=40.806862&lon=-96.681679&dist=10000&limit=150000&showLocations=0&showAtms=0"
    session = SgRequests()

    r = session.get(api_url)

    js = r.json()
    for j in js["branches"]:
        location_name = j.get("name")
        street_address = j.get("address1")
        city = j.get("city")
        state = "".join(j.get("address3")).split(",")[1].split()[0]
        page_url = "https://www.bankofcolorado.com/location-search"
        country_code = "US"
        postal = "".join(j.get("address3")).split(",")[1].split()[1]
        if postal.find("-") != -1:
            postal = postal.split("-")[0].strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        try:
            location_type = j.get("services")[0]
        except IndexError:
            location_type = "<MISSING>"
        if "".join(location_type).find("Full-Service") == -1:
            continue
        hours_of_operation = (
            " ".join(j.get("lobbyHours"))
            .replace("(By Appointment Only)", "")
            .replace("Free Parking Available", "")
            .strip()
        )
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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
