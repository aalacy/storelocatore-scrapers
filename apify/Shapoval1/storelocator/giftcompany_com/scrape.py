from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.giftcompany.com/"
    page_url = "https://www.giftcompany.com/pg/88/Store-Locator"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="store"]')
    for d in div:

        location_name = "".join(d.xpath("./*[1]//text()"))
        postal = "".join(
            d.xpath(
                './/li[contains(text(), "Manager")]/preceding-sibling::li[1]//text()'
            )
        )
        country_code = "UK"
        city = "".join(
            d.xpath(
                f'.//*[contains(text(), "{postal}")]/preceding::*[text()][1]//text()'
            )
        )
        if city.find(",") != -1:
            city = city.split(",")[0].strip()
        street_address = (
            " ".join(
                d.xpath("./*[1]/following-sibling::ul[1]//li[position()<3]//text()")
            )
            .replace("\n", "")
            .strip()
        )
        street_address = " ".join(street_address.split()) or "<MISSING>"
        if street_address == "<MISSING>":
            street_address = (
                " ".join(
                    d.xpath(
                        ".//h3/following-sibling::ul[1]/li[./span][position()<3]//text()"
                    )
                )
                .replace("\n", "")
                .strip()
            )
            street_address = " ".join(street_address.split()) or "<MISSING>"
        if street_address.find("Banbury,") != -1:
            street_address = street_address.split("Banbury,")[0].strip()
        phone = "".join(
            d.xpath(
                './/li[contains(text(), "Manager")]/following-sibling::li[1]//text()'
            )
        )
        hours_of_operation = (
            "Mon "
            + "".join(
                d.xpath(
                    './/*[text()="Opening Times"]/following-sibling::ul/li[1]//text() | .//h4[./*[contains(text(), "Opening Times")]]/following-sibling::ul/li[1]//text()'
                )
            )
            + " Tue "
            + "".join(
                d.xpath(
                    './/*[text()="Opening Times"]/following-sibling::ul/li[2]//text() | .//h4[./*[contains(text(), "Opening Times")]]/following-sibling::ul/li[2]//text()'
                )
            )
            + " Wed "
            + "".join(
                d.xpath(
                    './/*[text()="Opening Times"]/following-sibling::ul/li[3]//text() | .//h4[./*[contains(text(), "Opening Times")]]/following-sibling::ul/li[3]//text()'
                )
            )
            + " Thu "
            + "".join(
                d.xpath(
                    './/*[text()="Opening Times"]/following-sibling::ul/li[4]//text() | .//h4[./*[contains(text(), "Opening Times")]]/following-sibling::ul/li[4]//text()'
                )
            )
            + " Fri "
            + "".join(
                d.xpath(
                    './/*[text()="Opening Times"]/following-sibling::ul/li[5]//text() | .//h4[./*[contains(text(), "Opening Times")]]/following-sibling::ul/li[5]//text()'
                )
            )
            + " Sat "
            + "".join(
                d.xpath(
                    './/*[text()="Opening Times"]/following-sibling::ul/li[6]//text() | .//h4[./*[contains(text(), "Opening Times")]]/following-sibling::ul/li[6]//text()'
                )
            )
            + " Sun "
            + "".join(
                d.xpath(
                    './/*[text()="Opening Times"]/following-sibling::ul/li[7]//text() | .//h4[./*[contains(text(), "Opening Times")]]/following-sibling::ul/li[7]//text()'
                )
            )
        )

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)
