import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://gerritys.com"
    api_url = "https://gerritys.com/stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://gerritys.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = (
        "".join(tree.xpath('//script[contains(text(), "var locations = ")]/text()'))
        .split("var locations = ")[1]
        .split("S.mapManager")[0]
        .strip()
    )
    block = "".join(block[:-1])
    js = json.loads(block)
    for j in js:

        street_address = j.get("address1")
        phone = j.get("phone")
        city = j.get("city")
        postal = j.get("zipCode")
        state = j.get("state")
        country_code = "US"
        store_number = j.get("storeNumber")
        page_url = "https://gerritys.com/stores/"
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours = j.get("hourInfo") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if hours != "<MISSING>":
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//text()"))
                .replace("\n", "")
                .replace("\r", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(hours_of_operation.split()).replace("Store Hours", "").strip()
            )
            tmpt = "".join(a.xpath("//a/@href"))
            if tmpt:
                r = session.get(tmpt, headers=headers)
                tree = html.fromstring(r.text)
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//h2[text()="Regular Hours:"]/following-sibling::p[position() < 8]//text()'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
