from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.concordrx.com/"
    domain = "concordrx.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(text(), "Locations ")]/following-sibling::ul[1]//a/@href'
    )
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="pageTitle"]/text()')[0]
        raw_address = loc_dom.xpath(
            '//h2[contains(text(), "Our Location")]/following-sibling::div[1]//li//text()'
        )
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "re Open")]/following-sibling::div[1]//li/text()'
        )
        hoo = " ".join(hoo)
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2m3")[0]
            .split("!3d")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[1],
            zip_postal=raw_address[2],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1].split("!")[0],
            longitude=geo[0].split("!")[0],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
