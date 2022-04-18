# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep
from selenium.webdriver.common.keys import Keys

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    start_url = "https://www.leroymerlin.com.br/lojas"
    domain = "leroymerlin.com.br"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(15)
        elem = driver.find_element_by_name("city")
        elem.send_keys("Rio")
        sleep(10)
        driver.find_element_by_xpath('//*[contains(text(), "Rio Acima")]').click()
        sleep(10)
        driver.find_element_by_xpath('//button[@data-cy="confirm-button"]').send_keys(
            Keys.RETURN
        )
        sleep(15)

        dom = etree.HTML(driver.page_source)
        all_regions = dom.xpath('//a[@itemprop="url"]/@href')
        for url in all_regions:
            driver.get(url)
            sleep(5)
            dom = etree.HTML(driver.page_source)

            all_locations = dom.xpath(
                '//div[@class="content-thumbnail-picture"]/a[@class="link" and contains(@href, "loja")]/@href'
            )
            for page_url in all_locations:
                driver.get(page_url)
                sleep(3)
                loc_dom = etree.HTML(driver.page_source)
                location_name = loc_dom.xpath('//h1[@class="title-1"]/text()')[0]
                raw_address = loc_dom.xpath('//dd[@itemprop="streetAddress"]/text()')[0]
                city = loc_dom.xpath(
                    '//ul[@class="m-breadcrumbs"]//span[@itemprop="title"]/text()'
                )[-2].strip()
                if city == "Home":
                    addr = parse_address_intl(raw_address)
                    city = addr.city
                state = ""
                if len(raw_address.split(" - ")[-1]) == 2:
                    state = raw_address.split(" - ")[-1]
                zip_code = loc_dom.xpath('//dd[@itemprop="postalCode"]/text()')[0]
                phone = loc_dom.xpath('//dd[@itemprop="telephone"]/text()')
                phone = phone[0].split("/")[0].split("(")[0] if phone else ""
                geo = (
                    loc_dom.xpath('//iframe[@class="map"]/@src')[0]
                    .split("ll=")[-1]
                    .split("&")[0]
                    .replace(",,", ",")
                    .split(",")
                )
                if city and "Lojas" in city:
                    city = location_name

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=raw_address.split(" – ")[0].split(" - ")[0],
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code="",
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
