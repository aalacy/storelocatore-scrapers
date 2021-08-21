from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.ourbank.com/_/api/atms/45.6789447/-111.0340133/1000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["atms"]:

        page_url = "https://www.ourbank.com/locations"
        location_name = "".join(j.get("name")).strip()
        location_type = "ATM"
        net_name = j.get("networkName")
        if net_name == "First Security Bank ATMs":
            location_name = "First Security Bank"
        if net_name != "First Security Bank ATMs":
            location_name = (
                location_name.replace("First Security Bank", "")
                .replace("-", "")
                .strip()
            )
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
    locator_domain = "https://www.ourbank.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
