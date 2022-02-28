# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://scandinavian.com.ar/locales"
    domain = "scandinavian.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[h3[contains(text(), "Scandinavian Store")]]//div[@class="info-local"]'
    )
    all_locations += dom.xpath(
        '//div[h3[contains(text(), "Outlet")]]//div[@class="info-local"]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//span[@class="local-name"]/text()')[0]
        location_type = "Store"
        if "outlet" in location_name.lower():
            location_type = "Outlet"
        street_address = poi_html.xpath('.//span[@class="address-name"]/text()')[0]
        city = poi_html.xpath(
            './/span[@class="address-name"]/following-sibling::span[1]/text()'
        )[0].split(", ")[-1]
        phone = poi_html.xpath(
            './/span[@class="address-name"]/following-sibling::span[2]/text()'
        )[0]
        hoo = poi_html.xpath(
            './/span[@class="address-name"]/following-sibling::span[3]/text()'
        )
        hoo = hoo[0] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="",
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude="",
            longitude="",
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
