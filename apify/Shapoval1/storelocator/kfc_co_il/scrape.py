from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.co.il"
    api_url = "https://www.kfc.co.il/branches/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="page-content"]/div[1]/div/div/section[.//span[text()="Wi-Fi"]]/div/div/div'
    )
    for d in div:

        page_url = "https://www.kfc.co.il/branches/"
        location_name = "".join(
            d.xpath('.//a[text()="כתובת"]/preceding::p[1]/text()')
        ).strip()
        ad = "".join(d.xpath('.//a[text()="כתובת"]/following::p[1]/text()')).strip()
        street_address = (
            "".join(d.xpath('.//a[text()="כתובת"]/following::p[1]/text()')).strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>":
            continue
        country_code = "IL"
        phone = "".join(d.xpath('.//a[text()="טלפון"]/following::p[1]/text()')).strip()
        hours_of_operation = "".join(
            d.xpath('.//a[text()="שעות פתיחה"]/following::p[1]//text()')
        ).strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=SgRecord.MISSING,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
