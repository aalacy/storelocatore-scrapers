import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://marmishoes.com/storelocator"
    domain = "marmishoes.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@name="leftLocation"]//div[@class="amlocator-title"]/a[@class="amlocator-link"]/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        street_address = loc_dom.xpath(
            '//span[contains(text(), "Address: ")]/following-sibling::span[1]/text()'
        )[0]
        location_name = loc_dom.xpath('//h1[@class="page-title"]/span/text()')[0]
        city = loc_dom.xpath(
            '//span[contains(text(), "City: ")]/following-sibling::span[1]/text()'
        )[0]
        country_code = loc_dom.xpath(
            '//span[contains(text(), "Country: ")]/following-sibling::span[1]/text()'
        )[0]
        zip_code = loc_dom.xpath(
            '//span[contains(text(), "Zip: ")]/following-sibling::span[1]/text()'
        )[0]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        hoo = loc_dom.xpath('//div[@class="amlocator-schedule-table"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=re.findall("lat: (.+?),", loc_response.text)[0],
            longitude=re.findall("lng: (.+?),", loc_response.text)[0],
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
