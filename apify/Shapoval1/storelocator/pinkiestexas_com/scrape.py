from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pinkies.com"
    page_url = "https://pinkies.com/locations/"

    session = SgRequests()
    r = session.get(page_url)

    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//div[contains(@class,'et_pb_column et_pb_column_1_3')]//div[@class='et_pb_text_inner']"
    )
    for d in divs:
        location_name = "".join(d.xpath(".//h2/strong/text()"))
        block = d.xpath(".//p[./a]")
        for b in block:

            street_address = "".join(
                b.xpath(
                    ".//preceding-sibling::p[1]/strong/text() | .//preceding-sibling::p[2]/strong/text()"
                )
            )
            ad = (
                " ".join(b.xpath(".//preceding-sibling::p[1]/text()[1]"))
                .replace("\n", "")
                .strip()
            )
            city = ad.split(",")[0]
            postal = ad.split(",")[1].strip().split()[-1]
            state = ad.split(",")[1].strip().split()[0]
            if state.find("Texas") != -1:
                state = "TX"
            country_code = "US"
            phone = (
                "".join(b.xpath(".//preceding-sibling::p[1]/text()[2]"))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = (
                "".join(
                    b.xpath(
                        './/preceding::h2[./strong[contains(text(), "WE’RE OPEN")]]/strong/text()'
                    )
                )
                .replace("\n", "")
                .replace("WE’RE OPEN", "")
                .strip()
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
