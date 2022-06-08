import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgFirefox
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "evanscycles.com"
    start_url = "https://www.evanscycles.com/stores/all"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="letItems"]/a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url.lower())
        loc_response = session.get(page_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/span/text()")[0]
        street_address = loc_dom.xpath(
            '//div[@itemprop="address"]/following-sibling::div[1]/text()'
        )
        street_address = [elem.strip() for elem in street_address if elem.strip()]
        street_address = " ".join(street_address) if street_address else ""
        city = loc_dom.xpath(
            '//div[@itemprop="address"]/following-sibling::div[2]/text()'
        )
        city = city[0].strip() if city[0].strip() else ""
        zip_code = loc_dom.xpath(
            '//div[@itemprop="address"]/following-sibling::div[4]/text()'
        )
        zip_code = zip_code[0].strip() if zip_code else ""
        country_code = re.findall('countryCode":"(.+?)",', loc_response.text)[0]
        if country_code not in ["US", "GB", "CA"]:
            continue
        store_number = page_url.split("-")[-1]
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0].strip() if phone and phone[0].strip() else ""
        hours_of_operation = loc_dom.xpath(
            '//meta[@itemprop="openingHours"]/following-sibling::span/text()'
        )
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
