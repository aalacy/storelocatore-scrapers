from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.michels.com.au/"
    api_url = "https://www.michels.com.au/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="item-post clearfix"]')
    for d in div:

        page_url = "".join(d.xpath('.//h3[@class="entry-title"]/a/@href'))
        location_name = "".join(d.xpath('.//h3[@class="entry-title"]/a/text()'))
        street_address = (
            "".join(d.xpath('.//p[@class="address"]/text()[1]'))
            .replace("\n", "")
            .split(",")[2]
            .strip()
        )
        ad = (
            "".join(d.xpath('.//p[@class="address"]/text()[3]'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        state = ad.split()[0].strip()
        postal = ad.split()[1].strip()
        country_code = "AU"
        city = (
            "".join(d.xpath('.//p[@class="address"]/text()[2]'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        latitude = (
            "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
            .split("destination=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(d.xpath('.//a[text()="Get Directions"]/@href'))
            .split("destination=")[1]
            .split(",")[1]
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h5[text()="Opening Hours"]/following-sibling::ul/li//text()'
                )
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
