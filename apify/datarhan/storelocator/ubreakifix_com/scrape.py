from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "ubreakifix.com"
    start_url = "https://www.ubreakifix.com/locations"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_urls = dom.xpath('//div[@id="storelist"]//a/@href')
    canadian_url = "https://www.ubreakifix.com/ca/locations"
    ca_response = session.get(canadian_url)
    ca_dom = etree.HTML(ca_response.text)
    all_urls += ca_dom.xpath('//div[@id="storelist"]//a/@href')
    for url in list(set(all_urls)):
        if "#" in url:
            continue
        if "https" in url:
            continue
        store_url = "https://www.ubreakifix.com/" + url
        loc_response = session.get(store_url)
        if "asurion" in str(loc_response.url):
            continue
        loc_dom = etree.HTML(loc_response.text)
        com_soon = loc_dom.xpath('//div[contains(text(), "Coming Soon")]')
        if com_soon:
            continue

        location_name = " ".join(
            loc_dom.xpath('//h1[@class="title title--headline"]/text()')[0].split()
        )
        street_address = loc_dom.xpath('//p[@class="store-address"]/text()')[0].strip()
        raw_data = loc_dom.xpath('//p[@class="store-address"]/span/text()')
        phone = loc_dom.xpath('//span[@class="phone-link__text"]/text()')[0].strip()
        hoo = loc_dom.xpath(
            '//div[@class="store-hours show-above-m"]/p[@class="store-hours__details"]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=raw_data[0],
            state=raw_data[1],
            zip_postal=raw_data[2],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
