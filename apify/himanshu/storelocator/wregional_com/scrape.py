# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.wregional.com/main/physician-locator?atoz=1"
    domain = "wregional.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="phys-results-container"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(
            './/span[contains(text(), "Office Name:")]/following-sibling::span[1]/text()'
        )[0]
        street_address = poi_html.xpath(
            './/span[contains(text(), "Address:")]/following-sibling::span[1]/text()'
        )[0]
        city = poi_html.xpath(
            './/span[contains(text(), "City:")]/following-sibling::span[1]/text()'
        )
        city = city[0] if city else ""
        state = poi_html.xpath(
            './/span[contains(text(), "State:")]/following-sibling::span[1]/text()'
        )[0]
        zip_code = poi_html.xpath(
            './/span[contains(text(), "Postal Code:")]/following-sibling::span[1]/text()'
        )[0]
        phone = poi_html.xpath(
            './/span[contains(text(), "Phone:")]/following-sibling::span[1]/text()'
        )
        phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
