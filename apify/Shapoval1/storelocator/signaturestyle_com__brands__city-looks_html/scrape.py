from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.signaturestyle.com/"
    api_url = "https://www.signaturestyle.com/brands/city-looks.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="SALON DETAILS"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href")).replace("\n", "").strip()

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h2/text()"))
        location_type = "City Looks"
        street_address = "".join(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
        state = "".join(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
        postal = "".join(tree.xpath('//span[@itemprop="postalCode"]/text()'))
        country_code = "US"
        city = "".join(tree.xpath('//span[@itemprop="addressLocality"]/text()'))
        latitude = "".join(tree.xpath('//meta[@itemprop="latitude"]/@content'))
        longitude = "".join(tree.xpath('//meta[@itemprop="longitude"]/@content'))
        phone = "".join(tree.xpath('//span[@itemprop="telephone"]/a/text()'))
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[contains(@class, "salon-timings")]//meta[@itemprop="openingHours"]/@content'
                )
            )
            .replace("\n", "")
            .replace("Su  -", "Su  - Closed")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            location_type=location_type,
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
