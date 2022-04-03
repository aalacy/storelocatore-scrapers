from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.wendys.com.do"
    api_url = "https://www.wendys.com.do/donde-esta-wendy-s"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p[@style="font-size:19px;"]]')
    for d in div:

        page_url = "https://www.wendys.com.do/donde-esta-wendy-s"
        location_name = "".join(d.xpath("./p[1]//text()"))
        street_address = " ".join(d.xpath("./p[2]//text()")).replace("\n", "").strip()
        country_code = "Dominican Republic"
        city = "".join(d.xpath(".//preceding::h2[1]//text()"))
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/p[.//span[text()="Menú Regular"]]/following-sibling::p[./span[@style="font-family:futura-lt-w01-book,sans-serif;"]]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Delivery") != -1:
            hours_of_operation = hours_of_operation.split("Delivery")[0].strip()

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
