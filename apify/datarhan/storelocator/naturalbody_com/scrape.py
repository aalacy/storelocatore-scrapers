from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.naturalbody.com/spa-locations/locations"
    domain = "naturalbody.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[div[contains(text(), "Locations")]]/following-sibling::nav[1]//a/@href'
    )[1:]
    for page_url in all_locations:
        page_url = urljoin(start_url, page_url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@class="split-content hero-left"]/h2/text()'
        )
        location_name = location_name[0] if location_name else ""
        raw_address = loc_dom.xpath(
            '//div[@class="split-content hero-left"]//a/text()'
        )[:4]
        if "Book Now" in raw_address[-1]:
            raw_address = raw_address[:-1]
        if raw_address[-1].split("-")[0].isdigit():
            raw_address = raw_address[:-1]
        if len(raw_address) == 3:
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = loc_dom.xpath('//p/a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        geo = (
            loc_dom.xpath(
                '//div[@class="split-content hero-left"]//a[contains(@href, "maps")]/@href'
            )[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        latitude = geo[0]
        longitude = geo[1]
        days = loc_dom.xpath('//div[@class="w-layout-grid spa-hours"]//text()')[:7]
        hours = loc_dom.xpath('//div[@class="w-layout-grid spa-hours"]//text()')[7:]
        hoo = list(map(lambda d, h: d + " " + h, days, hours))
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
