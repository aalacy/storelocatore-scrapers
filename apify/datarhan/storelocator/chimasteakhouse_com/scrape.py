from lxml import etree
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.chimasteakhouse.com/"
    domain = "chimasteakhouse.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(text(), "Locations & Prices")]/following-sibling::ul[1]//a/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        raw_data = loc_dom.xpath('//div[@class="location-detail-wrapper"]/div/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if len(raw_data) == 2:
            city = location_name = raw_data[1].split(", ")[0]
            street_address = raw_data[0]
            state = raw_data[1].split(", ")[-1].split()[0]
            zip_code = raw_data[1].split(", ")[-1].split()[-1]
        else:
            addr = parse_address_intl(" ".join(raw_data))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            city = addr.city
            zip_code = addr.postcode
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[-1]
        hoo = loc_dom.xpath(
            '//p[label[contains(text(), "Hours of Operation:")]]/following-sibling::p[1]/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="hours-of-operation"]//text()')
        hoo = " ".join(hoo)

        with SgFirefox() as driver:
            driver.get(page_url)
            sleep(10)
            driver.switch_to.frame(
                driver.find_element_by_xpath('//iframe[contains(@src, "maps")]')
            )
            loc_dom = etree.HTML(driver.page_source)
            geo = (
                loc_dom.xpath('//a[contains(@href, "/@")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone=phone,
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
