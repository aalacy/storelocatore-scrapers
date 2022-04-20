import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.prouds.com.au/"
    page_url = "https://www.prouds.com.au/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var go_stores")]/text()'))
        .split("var go_stores =")[1]
        .split("//")[0]
        .strip()
    )
    div = "".join(div[:-1])
    js = json.loads(div)

    for j in js.values():

        location_name = j.get("name")
        try:
            ad = "".join(j.get("address")).split("\n")
        except:
            ad = []
        if not ad:
            continue
        adr = " ".join(ad).replace("\r", "").replace("&amp;amp;amp;", "").strip()
        a = parse_address(International_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "AU"
        city = location_name
        if str(city).find("(") != -1:
            city = str(city).split("(")[0].strip()
        if postal == "<MISSING>" and adr.split()[-1].isdigit():
            postal = adr.split()[-1].strip()
            state = adr.split()[-2].strip()
        store_number = j.get("storenumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phone")
        hours = j.get("openhours") or "<MISSING>"

        hours_of_operation = (
            "".join(hours)
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("\\u2013", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("{", "")
            .replace("}", "")
            .replace('"', "")
            .replace("hours:", " ")
        )
        if (
            hours_of_operation
            == "Sunday  ,Monday  ,Tuesday  ,Wednesday  ,Thursday  ,Friday  ,Saturday  "
        ):
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
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
