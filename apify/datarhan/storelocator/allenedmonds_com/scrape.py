import ssl
from time import sleep
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox
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
    session = SgRequests()
    domain = "allenedmonds.com"
    start_url = "https://www.allenedmonds.com/stores"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(15)
        driver.find_element_by_id("dwfrm_storelocator_maxdistance").click()
        sleep(2)
        driver.find_element_by_xpath('//option[@label="USA"]').click()
        sleep(2)
        driver.find_element_by_id("dwfrm_storelocator_postalCode").send_keys("10001")
        sleep(2)
        driver.find_element_by_name("dwfrm_storelocator_findbyzip").click()
        sleep(2)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[@class="store-link"]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@id="primary"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = loc_dom.xpath('//span[@itemprop="addressCountry"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        if country_code == "Italy":
            continue
        store_number = loc_dom.xpath('//input[@name="storeid"]/@value')
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = loc_dom.xpath("//div/@itemtype")[0].split("/")[-1]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//h2[contains(text(), "Hours:")]/following-sibling::p[2]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
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
