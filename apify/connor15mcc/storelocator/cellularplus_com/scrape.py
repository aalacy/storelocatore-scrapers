import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.cellularplus.com"
    api_url = "https://www.cellularplus.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    js_block = (
        "".join(tree.xpath('//script[contains(text(), "page.locations")]/text()'))
        .split("page.locations =")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(js_block)
    for j in js:

        location_name = j.get("Name") or "<MISSING>"
        street_address = f"{j.get('Address')} {j.get('Address2') or ''}".replace(
            "None", ""
        ).strip()
        state = j.get("ProvinceAbbrev") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = j.get("CountryCode") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        store_number = j.get("LocationId") or "<MISSING>"
        page_url = f"https://www.cellularplus.com/locations/{store_number}/{str(city).lower()}/"
        latitude = j.get("Position").get("Latitude") or "<MISSING>"
        longitude = j.get("Position").get("Longitude") or "<MISSING>"
        phone = j.get("Phone") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[text()="Hours of Operation"]/following-sibling::ul[1]/li//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
