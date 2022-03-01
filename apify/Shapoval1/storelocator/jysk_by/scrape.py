import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jysk.by"
    api_url = "https://jysk.by/stores"
    session = SgRequests()
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
        ids = j.get("id")
        info = j.get("popup_html")
        b = html.fromstring(info)
        ad = "".join(b.xpath('//div[@class="location-address"]/text()'))
        page_url = "https://jysk.by/stores"
        location_name = "".join(b.xpath('//div[@class="amlocator-title"]/text()'))
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "BY"
        city = a.city or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        hours_of_operation = (
            "".join(b.xpath('//div[@class="amlocator-description"]/text()'))
            .replace("График работы:", "")
            .replace("Склад хранения", "")
            .strip()
        )
        phone = "".join(
            tree.xpath(f'//div[@data-amid="{ids}"]/div[@class="location-phone"]/text()')
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
