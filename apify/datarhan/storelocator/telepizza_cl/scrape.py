import re
import ssl
from lxml import etree
from urllib.parse import urljoin
from time import sleep
from random import uniform

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    start_url = "https://www.telepizza.cl/pizzerias"
    domain = "telepizza.cl"

    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
        all_areas = dom.xpath('//ul[@class="areas"]/li/a/@href')
        for url in all_areas:
            area_url = urljoin(start_url, url)
            driver.get(area_url)
            sleep(uniform(1, 3))
            dom = etree.HTML(driver.page_source)
            all_cities = dom.xpath('//ul[@class="cities"]/li/a/@href')
            for url in all_cities:
                city_url = urljoin(area_url, url)
                driver.get(city_url)
                sleep(uniform(0, 5))
                dom = etree.HTML(driver.page_source)
                all_locations = dom.xpath('//ul[@class="list"]/li')
                for poi_html in all_locations:
                    page_url = poi_html.xpath(
                        './/a[@class="moreInfoLinkFromList"]/@href'
                    )
                    if not page_url:
                        page_url = poi_html.xpath("//@urltienda")
                    page_url = urljoin(area_url, page_url[0])
                    page_url = page_url.replace("/pizzerias/", "/pizzeria/")
                    driver.get(page_url)
                    sleep(uniform(3, 8))
                    loc_dom = etree.HTML(driver.page_source)
                    location_name = poi_html.xpath(".//h2/text()")
                    if not location_name:
                        location_name = loc_dom.xpath(
                            '//span[@class="heading-xl"]/strong/text()'
                        )
                    if not location_name:
                        continue
                    location_name = location_name[0].replace("Telepizza ", "")
                    raw_address = poi_html.xpath('.//p[@class="prs"]/text()')
                    if not raw_address:
                        raw_address = loc_dom.xpath("//address/span/text()")
                    raw_address = [e.strip() for e in raw_address if e.strip()]
                    city = raw_address[-1]
                    if city.startswith("."):
                        city = city[1:]
                    phone = poi_html.xpath(
                        './/p[span[@class="i_phone"]]/span[2]/text()'
                    )
                    if not phone:
                        phone = loc_dom.xpath('//span[@class="phoneFooter"]/text()')
                    phone = phone[0].strip() if phone else ""
                    if phone == "0" or phone == "123":
                        phone = ""
                    latitude = re.findall("lat = (.+?);", driver.page_source)[0]
                    if latitude == "0":
                        latitude = ""
                    longitude = re.findall("lng = (.+?);", driver.page_source)[0]
                    if longitude == "0":
                        longitude = ""
                    hoo = loc_dom.xpath(
                        '//h4[contains(text(), "A recoger")]/following-sibling::table//text()'
                    )
                    hoo = " ".join([e.strip() for e in hoo if e.strip()])

                    item = SgRecord(
                        locator_domain=domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=" ".join(raw_address[:-1]),
                        city=city,
                        state="",
                        zip_postal="",
                        country_code="ES",
                        store_number="",
                        phone=phone,
                        location_type="",
                        latitude=latitude,
                        longitude=longitude,
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
