import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "hercrentals.com"
    start_url = (
        "https://www.hercrentals.com/ca/locations/location_statewise_results.html"
    )
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_urls = dom.xpath('//ul[@class="hideEquips canadaStates"]//a/@href')
    all_urls = [elem for elem in all_urls if "javascript" not in elem]

    for store_url in all_urls:
        store_url = "https://www.hercrentals.com/" + store_url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//h1[@itemprop="name"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = store_dom.xpath('//p[@itemprop="streetAddress"]/text()')
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        city = store_dom.xpath('//input[@id="city"]/@value')
        city = city[0] if city else "<MISSING>"
        state = store_dom.xpath('//p[@itemprop="addressRegion"]/text()')
        if not state[0].strip():
            continue
        state = state[0].split(",")[-1].strip().split()[0] if state else "<MISSING>"
        zip_code = store_dom.xpath('//input[@id="branchZipCode"]/@value')[0]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_data = (
            store_dom.xpath('//script[contains(text(), "country")]/text()')[0]
            .replace("\r", "")
            .replace("\n", "")
        )
        country_code = re.findall("country:'(.+?)',", country_data)
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = re.findall(r"\((\d+)\)", location_name)
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = store_dom.xpath('//p[@itemprop="telephone"]/text()')
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = store_dom.xpath('//input[@id="latitude"]/@value')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath('//input[@id="longitude"]/@value')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = []
        hours_html = store_dom.xpath(
            '//div[@itemprop="openingHoursSpecification"]/table/tr'
        )
        for elem in hours_html:
            day = elem.xpath('.//td[@itemprop="dayOfWeek"]/text()')[0]
            opens = elem.xpath('.//time[@itemprop="opens"]/@content')[0]
            close = elem.xpath('.//time[@itemprop="closes"]/@content')[0]
            hours_of_operation.append("{} {} - {}".format(day, opens, close))
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
