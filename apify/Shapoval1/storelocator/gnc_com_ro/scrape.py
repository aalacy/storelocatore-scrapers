from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.gnc.com.ro/"
    api_url = "https://www.gnc.com.ro/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//span[text()="magazine"]/following-sibling::ul/li/a[@href]')
    for d in div:

        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://www.gnc.com.ro{slug}"
        city = "".join(d.xpath('.//preceding::a[@style="font-size: 16px;"][1]/text()'))

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//div[@class="std"]/div/p[1]//text()')).strip()
            or "<MISSING>"
        )
        street_address = (
            "".join(tree.xpath('//div[@class="std"]/div/p[2]//text()'))
            .replace(f", {city}", "")
            .strip()
            or "<MISSING>"
        )
        country_code = "RO"
        phone = (
            "".join(tree.xpath('//div[@class="std"]/div/p[3]//text()')).strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            "".join(tree.xpath('//div[@class="std"]/div/p[5]//text()')).strip()
            or "<MISSING>"
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
