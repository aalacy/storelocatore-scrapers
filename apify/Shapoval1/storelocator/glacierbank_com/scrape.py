from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://www.glacierbank.com/_/api/branches/48.1968612/-114.3136565/1000"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["branches"]:

        page_url = "https://www.glacierbank.com/locations"
        location_name = "".join(j.get("name")).strip()
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

        if (
            hours_of_operation.find("Hours") != -1
            and hours_of_operation.find("Drive") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Hours")[1].split("Drive")[0].strip()
            )
        if hours_of_operation.find("ATM") != -1:
            hours_of_operation = hours_of_operation.split("ATM")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("Lobby Hours", "")
            .replace(":   ", "")
            .replace("Hours", "")
            .strip()
        )

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
    locator_domain = "https://www.glacierbank.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
