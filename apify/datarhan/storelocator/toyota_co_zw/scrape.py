from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.co.zw/en/dealership/toyota-zimbabwe"
    domain = "toyota.co.zw"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="concessions"]//a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_address = loc_dom.xpath('//div[@class="location-info"]/div/text()')
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        types = loc_dom.xpath('//div[@class="concession-services"]//text()')
        types = [e.strip() for e in types if e.strip()]
        location_type = ", ".join(types)
        geo = loc_dom.xpath('//script[contains(text(), "map_markers")]/text()')[
            0
        ].split(",")[1:3]
        hoo = loc_dom.xpath(
            '//div[@class="concession-schedules"]/div[@class="item"]//text()'
        )
        hoo = " ".join(" ".join([e.strip() for e in hoo if e.strip()]).split())

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state="",
            zip_postal="",
            country_code="ZW",
            store_number="",
            phone=phone,
            location_type=location_type,
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
