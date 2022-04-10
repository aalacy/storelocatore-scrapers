from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.concordrx.com/"
    domain = "concordrx.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@href="/contact"]/following-sibling::ul//a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="pageTitle"]/text()')
        location_name = location_name[0] if location_name else ""
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else ""
        if (
            "Suite"
            in loc_dom.xpath('//span[@itemprop="streetAddress"]/following::text()')[1]
        ):
            street_address += (
                " "
                + loc_dom.xpath('//span[@itemprop="streetAddress"]/following::text()')[
                    1
                ].strip()
            )
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else ""
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else ""
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else ""
        phone = loc_dom.xpath('//p[@itemprop="telephone"]/text()')
        if not phone:
            phone = loc_dom.xpath('//li[contains(text(), "Phone:")]/text()')
        phone = phone[0].split(":")[-1].strip() if phone else ""
        hoo = loc_dom.xpath('//ul[@class="hours hours2"]//text()')
        if not hoo:
            hoo = loc_dom.xpath(
                '//li[contains(text(), "Fax:")]/following-sibling::li/text()'
            )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
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
