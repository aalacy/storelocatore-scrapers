import ssl
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgselenium import SgChrome
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    domain = "hibdontire.com"
    start_url = "https://local.hibdontire.com/"

    with SgChrome() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)
    all_locations = dom.xpath('//li[@itemtype="http://schema.org/LocalBusiness"]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h3/a/@href")[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath(".//h3/a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')
        city = city[0][:-1] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        phone = poi_html.xpath('.//a[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        hoo = poi_html.xpath('.//dl[@class="list-hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
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
