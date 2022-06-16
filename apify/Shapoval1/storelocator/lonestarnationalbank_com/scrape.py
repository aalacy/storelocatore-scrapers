import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.lonestarnationalbank.com/locations/"
    api_url = "https://www.lonestarnationalbank.com/a80ffd210dffea6c5cfb9968d6f0a5b18f5d9718-f36b062163847f5dc7c4.js"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath("//*//text()"))
        .split("parse('")[1]
        .split("')}}]);")[0]
        .replace("\\", "")
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:

        phone = j.get("phone") or "<MISSING>"
        street_address = j.get("streetAddress")
        city = j.get("city")
        state = j.get("state")
        location_name = "".join(j.get("name"))
        country_code = "US"
        latitude = j.get("geo")[1]
        longitude = j.get("geo")[0]
        location_type = j.get("category") or "<MISSING>"
        hours = j.get("lobbyHours")
        hoursM = j.get("motorBankHours")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("days")
                times = h.get("times")
                line = f"{day} {times}"
                tmp.append(line)

        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if location_type == "ATM":
            hours_of_operation = "24 hrs"
        if hours_of_operation == "<MISSING>":
            for h in hoursM:
                day = h.get("days")
                times = h.get("times")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = ";".join(tmp) or "<MISSING>"
        cms = j.get("comingSoon")
        if cms:
            hours_of_operation = "Coming Soon"
        if location_name.find("ATM") != -1:
            location_type = "ATM"
        postal = j.get("zipCode")
        page_url = "https://www.lonestarnationalbank.com/locations/"

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
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_TYPE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
