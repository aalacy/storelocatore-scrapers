# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.cinnabon.uk/stores"
    domain = "cinnabon.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        driver.switch_to.frame(driver.find_element_by_name("htmlComp-iframe"))
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="storelocator-store"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(
            './/a[@class="storelocator-viewlink storelocator-storename"]/text()'
        )[0]
        raw_addr = poi_html.xpath('.//p[@class="storelocator-address"]/text()')
        raw_addr = [e.strip() for e in raw_addr if e.strip()]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        hoo = poi_html.xpath('.//p[@class="storelocator-opening-daily "]//text()')
        hoo = " ".join([e.strip() for e in hoo])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_addr[-3],
            city=raw_addr[-2],
            state="",
            zip_postal=raw_addr[-1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
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
