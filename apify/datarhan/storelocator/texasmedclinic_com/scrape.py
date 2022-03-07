from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "texasmedclinic.com"
    start_url = "https://www.texasmedclinic.com/locations/"

    all_locations = []
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//ul[@class="locationList"]/li/a/@href')
    for url in all_cities:
        response = session.get(urljoin(start_url, url), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//ul[@class="locationList"]//div[@class="locImg"]/a/@href'
        )

    for store_url in all_locations:
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        c_soon = loc_dom.xpath('//strong[contains(text(), "OPENING LATE")]')
        if c_soon:
            continue

        location_name = loc_dom.xpath('//h1[@class="mainTitle entry-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//li[@class="locAddress"]/a/text()')[0].split(", ")
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[-1]
        phone = loc_dom.xpath('//a[@class="clickPhone"]/text()')
        phone = phone[0] if phone else ""
        hours_of_operation = loc_dom.xpath('//li[@class="locHours"]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
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
