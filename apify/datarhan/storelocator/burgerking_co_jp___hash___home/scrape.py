import re
import ssl
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgpostal.sgpostal import parse_address_intl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    start_url = "https://www.burgerking.co.jp/#/store"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgChrome() as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//ul[@class="list02"]/li')
    for poi_html in all_locations:
        location_name = poi_html.xpath('.//p[@class="tit"]/strong/text()')[0]
        addr = parse_address_intl(
            poi_html.xpath('.//div[@class="shop_detailinfo"]/dl[1]//span/text()')[0]
        )
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = poi_html.xpath(".//dd/p//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=SgRecord.MISSING,
            phone=poi_html.xpath(".//span//text()")[-1],
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
