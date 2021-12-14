import ssl
from time import sleep
from random import uniform
from lxml import etree
from urllib.parse import urljoin

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


def fetch_data():
    start_url = "https://sephora.ru/company/shops/"
    domain = "sephora.ru"

    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
        all_cities = dom.xpath('//div[@class="b-shops-cities__item"]/a/@href')
        for url in all_cities:
            city_url = urljoin(start_url, url)
            sleep(uniform(0, 5))
            driver.get(city_url)
            dom = etree.HTML(driver.page_source)

            all_locations = dom.xpath('//div[div[@class="b-shops__slider-item-city"]]')
            for poi_html in all_locations:
                location_name = poi_html.xpath(
                    './/div[@class="b-shops__slider-item-name"]/text()'
                )[0].strip()
                street_address = (
                    poi_html.xpath(
                        './/div[@class="b-shops__slider-item-contacts"]/text()'
                    )[0]
                    .split(":")[-1]
                    .strip()
                    .replace("\xa0", " ")
                    .strip()
                )
                city = poi_html.xpath(
                    './/div[@class="b-shops__slider-item-city"]/text()'
                )[0].strip()
                phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0].strip()
                geo = poi_html.xpath("@data-coords")[0][1:-1].split(",")
                raw_hoo = poi_html.xpath(
                    './/div[@class="b-shops__slider-item-contacts"]//text()'
                )
                raw_hoo = " ".join([e.strip() for e in raw_hoo if e.strip()])
                hoo = raw_hoo.split("Открыто:")[-1].strip()

                item = SgRecord(
                    locator_domain=domain,
                    page_url=city_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=SgRecord.MISSING,
                    zip_postal=SgRecord.MISSING,
                    country_code="RU",
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=SgRecord.MISSING,
                    latitude=geo[0],
                    longitude=geo[-1],
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
