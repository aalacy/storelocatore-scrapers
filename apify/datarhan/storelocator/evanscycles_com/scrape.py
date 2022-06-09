import demjson
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

        data = (
            loc_dom.xpath('//script[contains(text(), "store =")]/text()')[0]
            .split("store =")[1]
            .split(";\r\n    var")[0]
        )
        poi = data = demjson.decode(data)
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0].strip() if phone and phone[0].strip() else ""
        hours_of_operation = loc_dom.xpath(
            '//meta[@itemprop="openingHours"]/following-sibling::span/text()'
        )
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["town"],
            state=poi["county"],
            zip_postal=poi["postCode"],
            country_code=poi["countryCode"],
            store_number=poi["code"],
            phone=phone,
            location_type=poi["storeType"],
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
