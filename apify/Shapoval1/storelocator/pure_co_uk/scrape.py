from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pure.co.uk"
    api_url = "https://www.pure.co.uk/shops/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[@class="btn btn-outline-secondary"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//text()"))
        page_url = f"https://www.pure.co.uk{slug}"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        street_address = "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
        state = "<MISSING>"
        postal = "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
        country_code = "UK"
        city = "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
        latitude = (
            "".join(tree.xpath('//a[text()="View on Google Maps"]/@href'))
            .split("ll=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//a[text()="View on Google Maps"]/@href'))
            .split("ll=")[1]
            .split(",")[1]
            .strip()
        )
        phone = "".join(tree.xpath('//span[@itemprop="telephone"]/text()'))
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h4[text()="Opening Times"]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        tmpcls = "".join(
            tree.xpath('//p[contains(text(), "temporarily closed")]/text()')
        )
        if tmpcls:
            hours_of_operation = "Temporarily closed"

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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
