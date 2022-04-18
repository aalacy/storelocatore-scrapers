from lxml import etree
from urllib.parse import urljoin

from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    domain = "thelandinggroup.ca"
    start_url = "https://www.thelandinggroup.ca/en/locations/index.html"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath(
            '//a[contains(text(), "Locations")]/following-sibling::ul/li/a/@href'
        )
        for url in all_locations:
            store_url = urljoin(start_url, url)
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

            location_name = loc_dom.xpath('//h1/span[@class="Hero-geo"]/text()')[0]
            street_address = loc_dom.xpath(
                '//meta[@itemprop="streetAddress"]/@content'
            )[0]
            city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')[0]
            state = loc_dom.xpath('//abbr[@class="c-address-state"]/text()')[0]
            zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
            country_code = "CA"
            phone = loc_dom.xpath('//a[@class="Phone-link"]/text()')[0]
            latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
            longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
            hoo = loc_dom.xpath('//table[@class="c-hours-details"]//text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo).split("Hours")[-1] if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
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
