from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bankofcastile.com"
    api_url = "https://www.bankofcastile.com/_/api/branches/42.6340526/-78.0482979/5000"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["branches"]:

        page_url = "https://www.bankofcastile.com/locations"
        location_name = j.get("name")
        location_type = "Branch"
        street_address = j.get("address")
        phone = j.get("phone") or "<MISSING>"
        state = j.get("state")
        postal = j.get("zip")
        city = j.get("city")
        country_code = "US"
        latitude = j.get("lat")
        longitude = j.get("long")
        hours = j.get("description")
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath("//*//text()"))
            .replace("\n", "")
            .replace("Lobby Hours:", "Lobby Hours")
            .strip()
        )
        if (
            hours_of_operation.find("Lobby Hours") != -1
            and hours_of_operation.find("24 hour") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Lobby Hours")[1].split("24 hour")[0].strip()
            )
        if hours_of_operation.find("24-hour") != -1:
            hours_of_operation = hours_of_operation.split("24-hour")[0].strip()
        if hours_of_operation.startswith("Drive-up"):
            hours_of_operation = hours_of_operation.replace(
                "Drive-up Hours", ""
            ).strip()
        if hours_of_operation.find("Drive-up") != -1:
            hours_of_operation = hours_of_operation.split("Drive-up")[0].strip()
        hours_of_operation = hours_of_operation.replace("Lobby Hours", "").strip()
        if hours_of_operation.find("Limited") != -1:
            hours_of_operation = "<MISSING>"

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
