import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.lebeda.com"
    api_url = "https://www.lebeda.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(
            tree.xpath('//script[contains(text(), "var wpsl_locator_all = ")]/text()')
        )
        .split("var wpsl_locator_all = ")[1]
        .split(";")[0]
        .strip()
    )
    js = json.loads(jsblock)
    for j in js["locations"]:

        page_url = j.get("permalink")
        location_name = "".join(j.get("title"))
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        jsSingle = (
            "".join(
                tree.xpath(
                    '//script[contains(text(), "var wpsl_locator_single")]/text()'
                )
            )
            .split("var wpsl_locator_single = ")[1]
            .split(";")[0]
            .strip()
        )
        a = json.loads(jsSingle)
        street_address = a.get("address")
        postal = a.get("zip") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        country_code = "US"
        phone = (
            "".join(tree.xpath('//a[@class="btn wp-ada-external-popup"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//strong[text()="Open"]/following-sibling::text() | //strong[text()="Store Hours"]/following-sibling::text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
