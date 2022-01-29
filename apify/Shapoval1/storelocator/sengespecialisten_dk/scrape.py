import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sengespecialisten.dk"
    api_url = "https://www.sengespecialisten.dk/butikker"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(
            tree.xpath('//script[contains(text(), "var __CONTENT_CACHE =")]/text()')
        )
        .split("var __CONTENT_CACHE =")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(div)
    for j in js["page"]["stores"]:

        slug = j.get("url")
        page_url = f"https://www.sengespecialisten.dk{slug}"
        location_name = j.get("name1")
        street_address = j.get("address1")
        postal = j.get("postalCode")
        country_code = "DK"
        city = j.get("city")
        phone = j.get("phone") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = (
            "".join(
                tree.xpath('//script[contains(text(), "var __CONTENT_CACHE =")]/text()')
            )
            .split("var __CONTENT_CACHE =")[1]
            .split(";")[0]
            .strip()
        )
        latitude = div.split('"lat":')[1].split(",")[0].strip()
        longitude = div.split('"lng":')[1].split("}")[0].strip()
        tmp = []
        js = json.loads(div)
        for j in js["page"]["openHours"]:
            day = j.get("name")
            opens = j.get("open")
            closes = j.get("close")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
