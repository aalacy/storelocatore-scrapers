# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.farmaciasahumada.cl/storelocator"
    domain = "farmaciasahumada.cl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="stores"]/li')
    next_page = dom.xpath('//a[@class="action  next"]/@href')
    while next_page:
        response = session.get(next_page[0])
        dom = etree.HTML(response.text)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//ul[@class="stores"]/li')
        next_page = dom.xpath('//a[@class="action  next"]/@href')

    for poi_html in all_locations:
        location_name = raw_address = poi_html.xpath(".//h4/strong/text()")[0]
        if location_name == "Default Source":
            continue
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        geo = poi_html.xpath(".//a/@onclick")[0].split("Map(")[-1].split(",")[:2]
        hoo = poi_html.xpath('.//p[@class="store-schedule"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        city = addr.city
        if city and len(city) < 4:
            city = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="TH",
            store_number="",
            phone="",
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
