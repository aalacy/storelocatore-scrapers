from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bootbarn.com"
    start_url = "https://www.bootbarn.com/stores-all"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_stores = dom.xpath('//div[@class="store"]/div/a/@href')
    for url in all_stores:
        store_url = "https://www.bootbarn.com" + url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//h1[@class="section-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = store_dom.xpath(
            '//address/span[@class="store-address1"]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = store_dom.xpath('//address/span[@class="store-address-city"]/text()')
        city = city[0].replace(",", "") if city else "<MISSING>"
        state = store_dom.xpath('//address/span[@class="store-address-state"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = store_dom.xpath(
            '//address/span[@class="store-address-postal-code"]/text()'
        )
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = store_url.split("=")[-1]
        phone = store_dom.xpath('//span[@class="store-phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        latitude = store_dom.xpath('//div[@id="store-detail-coords"]/@data-lat')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath('//div[@id="store-detail-coords"]/@data-lon')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath('//div[@class="store-hours-days"]//text()')
        hours_of_operation = [elem.strip() for elem in hours_of_operation if elem.strip]
        hours_of_operation = (
            " ".join(hours_of_operation).split("   Mon:")[0].strip()
            if hours_of_operation
            else "<MISSING>"
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
