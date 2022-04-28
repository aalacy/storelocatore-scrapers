from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "heinens.com"
    start_urls = [
        "https://www.heinens.com/stores/?state=OH&near=&ref=&lat=&lng=&range=10",
        "https://www.heinens.com/stores/?state=IL&near=&ref=&lat=&lng=&range=10",
    ]
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = []
    for start_url in start_urls:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//h2/a[contains(@href, "/stores/")]/@href')
        next_page = dom.xpath('//a[@class="next page-numbers"]/@href')
        while next_page:
            response = session.get(next_page[0], headers=hdr)
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//h2/a[contains(@href, "/stores/")]/@href')
            next_page = dom.xpath('//a[@class="next page-numbers"]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="page-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//meta[@itemprop="addressRegion"]/@content')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//meta[@itemprop="postalCode"]/@content')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="datum phone"]//a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath('//div[@class="datum hours"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation).replace("Store Hours ", "")
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
