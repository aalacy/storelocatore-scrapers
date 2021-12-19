from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):
    locator_domain = "https://www.gnc.co.th"
    page_url = "https://www.gnc.co.th/store-locations"
    with SgFirefox() as driver:

        driver.get(page_url)
        a = driver.page_source
        tree = html.fromstring(a)
        div = tree.xpath('//div[./div[@class="btn-section"]]')
        for d in div:

            phone = (
                " ".join(d.xpath('.//p/span[contains(text(), "โทรศัพท์")]//text()'))
                .replace("\n", "")
                .replace("โทรศัพท์ :", "")
                .strip()
            )
            street_address = "".join(d.xpath("./h2/text()")) or "<MISSING>"
            country_code = "TH"
            location_name = "<MISSING>"
            latitude = (
                "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
                .split("q=")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
                .split("q=")[1]
                .split(",")[1]
                .split("&")[0]
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    d.xpath('.//p/span[not(contains(text(), "โทรศัพท์"))]//text()')
                )
                .replace("\n", "")
                .strip()
                or "<MISSING>"
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
