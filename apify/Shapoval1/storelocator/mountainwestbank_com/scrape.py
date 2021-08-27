from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = (
        "https://www.mountainwestbank.com/_/api/branches/47.6955067/-116.7869971/500"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["branches"]:

        page_url = "https://www.mountainwestbank.com/locations"
        location_name = j.get("name")
        location_type = "Branch"
        street_address = "".join(j.get("address"))
        if street_address.find("\n") != -1:
            street_address = street_address.split("\n")[1].strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = "USA"
        city = j.get("city")
        latitude = j.get("lat")
        longitude = j.get("long")
        phone = j.get("phone")
        hours_of_operation = j.get("description")
        a = html.fromstring(hours_of_operation)
        hours_of_operation = " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
        if (
            hours_of_operation.find("Lobby") != -1
            and hours_of_operation.find("Drive-Up") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Lobby Hours")[1].split("Drive")[0].strip()
            )
        hours_of_operation = hours_of_operation.replace("Lobby Hours", "").strip()
        if hours_of_operation.find("ATM") != -1:
            hours_of_operation = hours_of_operation.split("ATM")[0].strip()
        if hours_of_operation.find("Office") != -1:
            hours_of_operation = (
                hours_of_operation.split("Office Hours:")[1]
                .split("Local:")[0]
                .replace("(PST)", "")
                .strip()
            )
        if hours_of_operation.find("Local:") != -1:
            hours_of_operation = "<MISSING>"
        hours_of_operation = hours_of_operation.replace("Hours:", "").strip()

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
    locator_domain = "https://www.mountainwestbank.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
