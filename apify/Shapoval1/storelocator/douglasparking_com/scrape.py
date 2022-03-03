import json
from sgscrape.sgpostal import USA_Best_Parser, parse_address
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.douglasparking.com"
    api_url = "http://www.douglasparking.com/locations-2/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "var bgmpData")]/text()'))
        .split("markers : ")[1]
        .split("};")[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js:

        page_url = "http://www.douglasparking.com/locations-2/"
        location_name = (
            "".join(j.get("title")).replace("&#038;", "&").replace("&#8211;", "–")
            or "<MISSING>"
        )
        info = j.get("details")
        if "HEADQUARTERS" in info:
            continue
        a = html.fromstring(info)
        ad = " ".join(a.xpath("//*//text()")).replace("\r\n", "").strip()

        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        if state == "On Jefferson":
            state = "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = "<MISSING>"
        if location_name.find("Oakland") != -1 or location_name.find("OAKLAND") != -1:
            city = "Oakland"
        if location_name.find("PORTLAND") != -1:
            city = "Portland"
        if location_name.find("MOUNTAIN VIEW") != -1:
            city = "Mountain view"

        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
