from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.myfarmers.bank/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(
        "https://www.myfarmers.bank/_/api/branches/33.26738640000001/-93.239115/500",
        headers=headers,
    )
    js = r.json()
    for j in js["branches"]:

        page_url = "https://www.myfarmers.bank/resources/locations-hours"
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        country_code = "US"
        latitude = j.get("lat")
        longitude = j.get("long")
        location_type = "Branch"

        phone = j.get("phone") or "<MISSING>"
        desc = j.get("description") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if desc != "<MISSING>":
            h = html.fromstring(desc)
            hours_of_operation = " ".join(h.xpath("//*//text()"))
            hours_of_operation = " ".join(hours_of_operation.split())

        if hours_of_operation.find("Lobby Hours") != -1:
            hours_of_operation = (
                hours_of_operation.split("Lobby Hours")[1].split("Services")[0].strip()
            )
        if (
            hours_of_operation.find("Hours") != -1
            and hours_of_operation.find("Services") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Hours")[1].split("Services")[0].strip()
            )
        if (
            hours_of_operation.find("Live Teller Hours") != -1
            and hours_of_operation.find("24/7 ATM") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Live Teller Hours")[1]
                .split("24/7 ATM")[0]
                .strip()
            )
        if hours_of_operation.find("Drive-Thru") != -1:
            hours_of_operation = hours_of_operation.split("Drive-Thru")[0].strip()
        if hours_of_operation.find("Drive-thru") != -1:
            hours_of_operation = hours_of_operation.split("Drive-thru")[0].strip()
        hours_of_operation = hours_of_operation.replace(": Monday", "Monday")

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
