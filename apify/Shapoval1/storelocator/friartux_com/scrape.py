from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.friartux.com"
    page_url = "https://www.friartux.com/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="place go-to-place"]')
    for d in div:

        location_name = "".join(d.xpath('.//span[@itemprop="name"]/text()')).strip()
        street_address = "".join(
            d.xpath('.//span[@itemprop="streetAddress"]/text()')
        ).strip()
        state = "".join(d.xpath('.//span[@itemprop="addressRegion"]/text()')).strip()
        postal = "".join(d.xpath('.//span[@itemprop="postalCode"]/text()')).strip()
        country_code = "US"
        city = (
            "".join(d.xpath('.//span[@itemprop="addressLocality"]/text()'))
            .replace(",", "")
            .strip()
        )
        store_number = "".join(d.xpath("./@id"))
        latitude = (
            "".join(
                d.xpath(
                    './/following::script[contains(text(), "pointofsale.places")]/text()'
                )
            )
            .split(f'"id":"{store_number}"')[1]
            .split('"lat":"')[1]
            .split('"')[0]
            .strip()
        )
        longitude = (
            "".join(
                d.xpath(
                    './/following::script[contains(text(), "pointofsale.places")]/text()'
                )
            )
            .split(f'"id":"{store_number}"')[1]
            .split('"lng":"')[1]
            .split('"')[0]
            .strip()
        )
        phone = "".join(d.xpath('.//span[@itemprop="telephone"]/text()'))
        hours_of_operation = (
            " ".join(d.xpath('.//meta[@itemprop="openingHours"]/@content'))
            .replace("\n", "")
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
            store_number=store_number,
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
