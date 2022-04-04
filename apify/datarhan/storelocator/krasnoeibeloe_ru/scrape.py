# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://krasnoeibeloe.ru/address/"
    domain = "krasnoeibeloe.ru"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        try:
            driver.find_element_by_xpath(
                '//a[@class="btn btn_red age_popup_btn age_popup_btn--agree"]'
            ).click()
        except Exception:
            pass
        all_regions = driver.find_elements_by_xpath(
            '//select[@name="region"]/following-sibling::div[1]//div[@class="option"]'
        )

        for i1, r in enumerate(all_regions[0:1]):
            all_regions = driver.find_elements_by_xpath(
                '//select[@name="region"]/following-sibling::div[1]//div[@class="option"]'
            )
            driver.find_element_by_xpath('//div[@class="item_select_city"]').click()
            try:
                driver.find_element_by_xpath(
                    '//a[@class="btn btn_red age_popup_btn age_popup_btn--agree"]'
                ).click()
            except Exception:
                pass
            driver.find_element_by_xpath('//div[@class="item_select_city"]').click()
            sleep(5)
            all_regions[i1].click()
            sleep(5)
            driver.find_element_by_xpath(
                '//div[@class="bl_selects_city"]/div[2]'
            ).click()
            sleep(5)
            dom = etree.HTML(driver.page_source)
            all_locations = dom.xpath('//div[contains(@class, "shop_list_row")]')
            for poi_html in all_locations:
                raw_data = poi_html.xpath(".//text()")
                raw_data = [e.strip() for e in raw_data if e.strip()]
                store_number = poi_html.xpath(".//input/@value")[0]
                city = dom.xpath('//select[@name="city"]/option/text()')
                city = city[0] if city else ""
                state = dom.xpath('//select[@name="region"]/option/text()')[0]
                hoo = poi_html.xpath('.//div[@class="shop_l_time"]/div/text()')
                hoo = " ".join([e.strip() for e in hoo])
                street_address = raw_data[0].replace("&quot;", '"')

                item = SgRecord(
                    locator_domain=domain,
                    page_url=start_url,
                    location_name="",
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal="",
                    country_code="RU",
                    store_number=store_number,
                    phone="",
                    location_type="",
                    latitude="",
                    longitude="",
                    hours_of_operation=hoo,
                )

                yield item

            all_cities = driver.find_elements_by_xpath(
                '//select[@name="city"]/following-sibling::div[1]//div[@class="option"]'
            )
            for i2, c in enumerate(all_cities):
                all_cities = driver.find_elements_by_xpath(
                    '//select[@name="city"]/following-sibling::div[1]//div[@class="option"]'
                )
                all_cities[i2].click()
                sleep(5)
                dom = etree.HTML(driver.page_source)
                all_locations = dom.xpath('//div[contains(@class, "shop_list_row")]')
                for poi_html in all_locations:
                    raw_data = poi_html.xpath(".//text()")
                    raw_data = [e.strip() for e in raw_data if e.strip()]
                    store_number = poi_html.xpath(".//input/@value")[0]
                    city = dom.xpath('//select[@name="city"]/option/text()')[0]
                    state = dom.xpath('//select[@name="region"]/option/text()')[0]

                    item = SgRecord(
                        locator_domain=domain,
                        page_url=start_url,
                        location_name="",
                        street_address=raw_data[0],
                        city=city,
                        state=state,
                        zip_postal="",
                        country_code="RU",
                        store_number=store_number,
                        phone="",
                        location_type="",
                        latitude="",
                        longitude="",
                        hours_of_operation=raw_data[1],
                    )

                    yield item
                driver.find_element_by_xpath(
                    '//div[@class="bl_selects_city"]/div[2]'
                ).click()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
