from lxml import etree
from time import sleep

from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    start_url = "https://jewelryexchange.com/contact-us/"
    domain = "jewelryexchange.com"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)

        all_locations = dom.xpath('//h3[@class="location-title"]/a/@href')
        for store_url in all_locations:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

            raw_data = loc_dom.xpath(
                '//div[@class="wpsl-location-address"]/span/text()'
            )
            raw_data = [e.strip() for e in raw_data if e.strip()]
            location_name = loc_dom.xpath(
                '//div[@class="wpsl-locations-details"]/span/strong/text()'
            )[0]
            if "Business Closed" in location_name:
                continue
            street_address = raw_data[0]
            city = raw_data[1].split(", ")[0]
            if "Store Closed" in city:
                continue
            if city.endswith(","):
                city = city[:-1]
            state = raw_data[2]
            zip_code = raw_data[3]
            phone = loc_dom.xpath('//div[@class="wpsl-contact-details"]//a/text()')
            phone = phone[0] if phone else ""
            geo = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("!2d")[-1]
                .split("!3m")[0]
                .split("!3d")
            )
            hoo = loc_dom.xpath('//table[@class="wpsl-opening-hours"]//text()')
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="United States",
                store_number="",
                phone=phone,
                location_type="",
                latitude=geo[1].split("!")[0],
                longitude=geo[0],
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
