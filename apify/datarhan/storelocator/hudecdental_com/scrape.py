# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://hudecdental.com/office-locations/"
    domain = "hudecdental.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View Location Details")]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_data = loc_dom.xpath('//div[@class="location_bar_2"]/div/text()')
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "Office Hours")]/following-sibling::h4//text()'
        )
        hoo = " ".join([e.strip() for e in hoo])

        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(10)
            driver.switch_to.frame(
                driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
            )
            loc_dom = etree.HTML(driver.page_source)
        geo = (
            loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=raw_data[1].split(", ")[0],
            state=" ".join(raw_data[1].split(", ")[-1].split()[:-1]),
            zip_postal=raw_data[1].split(", ")[-1].split()[-1],
            country_code="",
            store_number="",
            phone=raw_data[-1],
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
