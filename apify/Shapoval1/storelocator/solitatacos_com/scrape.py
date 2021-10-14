from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://solitatacos.com/"
    api_url = "https://solitatacos.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//ul[@data-menu="submenu-406"]/li/a')
    for b in block:

        page_url = "".join(b.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(
            tree.xpath('//h1[@class="hero__heading heading"]/text()')
        )
        adr = "".join(
            tree.xpath(
                '//p[.//a[contains(@href, "tel")]]/preceding-sibling::p[1]//text()'
            )
        )

        street_address = adr.split(",")[0].strip()
        phone = "".join(tree.xpath('//p//a[contains(@href, "tel")]/text()'))
        try:
            state = adr.split(",")[2].split()[0]
            postal = adr.split(",")[2].split()[-1]
            country_code = "USA"
            city = adr.split(",")[1].strip()
        except:
            state = "<MISSING>"
            postal = "<MISSING>"
            country_code = "US"
            city = "<MISSING>"
            street_address = "<MISSING>"
            phone = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./strong[contains(text(), "Hours of Operations")]]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        cms = "".join(tree.xpath('//h3[contains(text(), "COMING SOON")]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
