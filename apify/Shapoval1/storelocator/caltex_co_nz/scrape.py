import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://caltex.co.nz"
    api_url = "https://caltex.co.nz/station-finder/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "window._stations =")]/text()'))
        .split("window._stations =")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)
    for j in js:

        page_url = "https://caltex.co.nz/station-finder/"
        location_name = j.get("Name") or "<MISSING>"
        location_type = j.get("Type") or "<MISSING>"
        street_address = j.get("Street") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Postcode") or "<MISSING>"
        country_code = "NZ"
        city = j.get("City") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("Phone") or "<MISSING>"
        hours_of_operation = "".join(j.get("Hours")) or "<MISSING>"
        if hours_of_operation.find("LPG Filling") != -1:
            hours_of_operation = hours_of_operation.split("LPG Filling")[0].strip()
        if hours_of_operation.find(", Public") != -1:
            hours_of_operation = hours_of_operation.split(", Public")[0].strip()

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
