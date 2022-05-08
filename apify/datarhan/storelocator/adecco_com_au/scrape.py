# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome


def fetch_data():
    session = SgRequests()

    start_url = "https://www.adecco.com.au/our-locations/"
    domain = "adecco.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-list"]//a/@href')
    with SgChrome() as driver:
        for url in all_locations:
            page_url = urljoin(start_url, url)
            driver.get(page_url)
            sleep(15)
            try:
                driver.switch_to.frame(
                    driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
                )
            except Exception:
                continue
            loc_dom = etree.HTML(driver.page_source)
            raw_address = loc_dom.xpath('//div[@class="address"]/text()')[0]
            geo = (
                loc_dom.xpath('//a[@class="navigate-link"]/@href')[0]
                .split("@")[-1]
                .split(",")[:2]
            )
            loc_response = session.get(page_url, headers=hdr)
            if str(loc_response.url) == "https://www.adecco.com.au/":
                continue
            loc_dom = etree.HTML(loc_response.text)
            location_name = loc_dom.xpath('//div[@class="contact-meta-info"]/h6/text()')
            location_name = location_name[0].strip() if location_name else ""
            if not location_name:
                location_name = loc_dom.xpath("//h1/text()")[0]
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_address.split(", ")[0],
                city=" ".join(raw_address.split(", ")[-1].split()[:-2]),
                state="",
                zip_postal=raw_address.split(", ")[-1].split()[-1],
                country_code="AU",
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
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
