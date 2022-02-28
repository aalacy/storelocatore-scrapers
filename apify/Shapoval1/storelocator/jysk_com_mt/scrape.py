from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jysk.com.mt"
    api_url = "https://jysk.com.mt/stores-and-opening-hours/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//h3[contains(text(), "Store Details")]/following-sibling::p[not(./a)]'
    )
    for d in div:

        page_url = "https://jysk.com.mt/stores-and-opening-hours/"
        location_name = "".join(d.xpath("./text()[1]")).replace("\n", "").strip()
        street_address = "".join(d.xpath("./text()[2]")).replace("\n", "").strip()
        country_code = "MT"
        city = "".join(d.xpath("./text()[3]")).replace("\n", "").split(",")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/preceding::h3[text()="OPENING HOURS"]/following-sibling::table//tr/td/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
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
