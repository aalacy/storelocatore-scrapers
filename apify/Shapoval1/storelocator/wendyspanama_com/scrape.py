from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://wendyspanama.com/"
    page_url = "http://wendyspanama.com/restaurantes.jsp"
    with SgFirefox() as driver:
        driver.get(page_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//div[@class="col-md-4 col-sm-12"]')
        for d in div:

            location_name = "".join(d.xpath(".//h2//text()"))
            street_address = "".join(
                d.xpath(
                    './/p[contains(text(), "Horario")]/preceding-sibling::p[1]/text()'
                )
            )
            country_code = "PA"
            hours_of_operation = (
                " ".join(d.xpath('.//p[contains(text(), "PM")]/text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
