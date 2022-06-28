from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.harveynorman.hr/"
    page_url = "https://www.harveynorman.hr/gdjesmo"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="poslovalnica-urnik poslovalnica-urnik-l"]')
    for d in div:

        location_name = (
            "".join(
                d.xpath(
                    './/preceding-sibling::div[@class="poslovalnica-title"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        street_address = (
            "".join(d.xpath('.//p[@class="ext"]/a/text()[1]')).replace("\n", "").strip()
        )
        ad = (
            "".join(d.xpath('.//p[@class="ext"]/a/text()[2]')).replace("\n", "").strip()
        )
        postal = " ".join(ad.split()[:-1])
        country_code = "HR"
        city = ad.split()[-1].strip()
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Tel:")]/text()[1]'))
            .replace("Tel:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath('.//p[contains(text(), "0h")]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)

    locator_domain = "https://www.harveynorman.si/"
    page_url = "https://www.harveynorman.si/poslovalnice"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="poslovalnica-urnik poslovalnica-urnik-l"]')
    for d in div:
        location_name = (
            "".join(
                d.xpath(
                    './/preceding-sibling::div[@class="poslovalnica-title"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        street_address = (
            "".join(d.xpath('.//p[@class="ext"]//text()[1]'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        ad = "".join(d.xpath('.//p[@class="ext"]//text()[2]')).replace("\n", "").strip()
        postal = ad.split()[0].strip()
        country_code = "SI"
        city = "".join(ad.split()[1:])
        phone = (
            "".join(
                d.xpath(
                    './/p[contains(text(), "Tel:")]/text()[1] | .//p[contains(text(), "Tel")]/a/text()'
                )
            )
            .replace("Tel:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                d.xpath('.//p[contains(text(), "Tel:")]/preceding-sibling::p//text()')
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
