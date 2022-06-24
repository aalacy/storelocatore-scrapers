import json
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    domain = "koa.com"
    start_url = "https://koa.com/campgrounds/"
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_urls = dom.xpath('//ul[@class="zebra-list"]/li/div//a/@href')
        for url in all_urls:
            page_url = "https://koa.com" + url
            driver.get(page_url)
            loc_dom = etree.HTML(driver.page_source)
            poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
            poi = json.loads(poi)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=poi["address"]["streetAddress"],
                city=poi["address"]["addressLocality"],
                state=poi["address"]["addressRegion"],
                zip_postal=poi["address"]["postalCode"],
                country_code=poi["address"]["addressCountry"],
                store_number="",
                phone=poi["telephone"],
                location_type="",
                latitude=poi["geo"]["latitude"],
                longitude=poi["geo"]["longitude"],
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
