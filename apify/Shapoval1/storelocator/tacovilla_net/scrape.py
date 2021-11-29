from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    api_url = "https://tacovilla.net/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location"]')
    for d in div:

        page_url = "https://tacovilla.net/locations/"
        location_name = "".join(d.xpath(".//h2/text()"))
        street_address = "".join(d.xpath('.//span[@itemprop="streetAddress"]/text()'))
        state = "".join(d.xpath('.//span[@itemprop="addressRegion"]/text()'))
        postal = (
            "".join(d.xpath('.//div[@itemprop="address"]/text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        country_code = "US"
        city = "".join(d.xpath('.//span[@itemprop="addressLocality"]/text()'))
        phone = (
            "".join(d.xpath('.//span[@itemprop="telephone"]/a/text()'))
            .replace("\n", "")
            .strip()
        )
        latitude = (
            "".join(
                d.xpath(
                    f'.//preceding::div[./p/a[contains(text(), "{phone}")]][1]/@data-lat'
                )
            )
            or "<MISSING>"
        )
        longitude = (
            "".join(
                d.xpath(
                    f'.//preceding::div[./p/a[contains(text(), "{phone}")]][1]/@data-lng'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(d.xpath('.//span[@class="open-hours"]/@content'))
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
    locator_domain = "https://tacovilla.net"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
