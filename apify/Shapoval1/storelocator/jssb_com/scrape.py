import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jssb.com"
    api_url = "https://www.jssb.com/locations/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var oCenter")]/text()'))
        .split("console.log(")[1]
        .split(");")[0]
    )

    js = json.loads(jsblock)

    for j in js:

        page_url = "https://www.jssb.com/locations/"
        location_name = "".join(j.get("LocCustomerName"))
        street_address = f"{j.get('LocAddress')} {j.get('LocAddress2') or ''}".replace(
            "<br>", " "
        ).strip()
        city = j.get("LocCity")
        state = j.get("LocState")
        country_code = j.get("LocCountry")
        postal = j.get("LocZip")
        latitude = j.get("LocLatitude")
        longitude = j.get("LocLongitude")
        location_type = j.get("LocBranchOrAtm")
        if location_type == "atm":
            continue
        hours = j.get("LocHours") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            hours = html.fromstring(hours)
            hours_of_operation = (
                " ".join(hours.xpath("//*//text()")).replace("\n", "").strip()
            )
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()
        phone = j.get("LocPhoneNumber") or "<MISSING>"

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
