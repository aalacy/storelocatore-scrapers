import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jysk.lt"
    api_url = "https://www.jysk.lt/parduotuves"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "jsonLocations")]/text()'))
        .split("jsonLocations:")[1]
        .split("imageLocations")[0]
        .strip()
    )
    js_block = js_block[:-1]
    js = json.loads(js_block)
    for j in js["items"]:

        page_url = "https://www.jysk.lt/parduotuves"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "LT"
        city = j.get("city") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = (
            "".join(j.get("phone")).replace("Klientų aptarnavimas", "").strip()
            or "<MISSING>"
        )
        desc = "".join(j.get("description"))
        a = html.fromstring(desc)
        hours_of_operation = (
            " ".join(a.xpath("//*//text()"))
            .replace("\n", "")
            .replace("Parduotuvės darbo laikas", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .replace("Darba laiks Galvenā noliktava", "")
            .strip()
            or "<MISSING>"
        )
        ad = f"{street_address} {city}, {state} {postal}"

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
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
