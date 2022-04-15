# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://www.boscovsoptical.com/stores/"
    domain = "boscovsoptical.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@class, "store-info")]//h4/a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@itemprop="name"]/text()')[0]
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')[0]
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        phone = loc_dom.xpath('//a[@class="phone"]/text()')[0].strip()
        hoo = loc_dom.xpath('//p[@class="hours"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(5)
            driver.switch_to.frame(
                driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
            )
            loc_dom = etree.HTML(driver.page_source)

        geo = (
            loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
            .split("?ll=")[-1]
            .split("&")[0]
            .split(",")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
