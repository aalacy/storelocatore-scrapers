import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://beyondjuiceryeatery.com/"
    api_url = "https://beyondjuiceryeatery.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(tree.xpath('//script[contains(text(), "var map_positions =")]/text()'))
        .split("var map_positions =")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)
    for j in js:

        a = j.get("position_on_the_map")
        str_number = a.get("street_number")
        page_url = "https://beyondjuiceryeatery.com/locations/"
        location_name = "".join(
            tree.xpath(
                f'//p[contains(text(), "{str_number}")]/preceding-sibling::p[1]/text()'
            )
        )
        street_address = f"{a.get('street_number')} {a.get('street_name')}".strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("post_code") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        latitude = a.get("lat") or "<MISSING>"
        longitude = a.get("lng") or "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    f'//p[contains(text(), "{str_number}")]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        phone = " ".join(phone.split())
        hours_of_operation = (
            "".join(
                tree.xpath(
                    f'//p[contains(text(), "{str_number}")]/following-sibling::div[@class="ol-oh"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if location_name.find("SHELBY TOWNSHIP") != -1:
            city = location_name.split("(")[0].capitalize().strip()
        if phone == "TEMPORARILY CLOSED":
            phone = "<MISSING>"
            hours_of_operation = (
                hours_of_operation.capitalize().replace(":", "").strip()
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
            location_type=SgRecord.MISSING,
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
