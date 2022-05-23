# -*- coding: utf-8 -*-
from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.westelm.com.au/store-locations"
    domain = "westelm.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "STORE HOURS & DETAILS")]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_address = loc_dom.xpath(
            '//h3[contains(text(), "Address:")]/following-sibling::p[1]/text()'
        )
        raw_address = [e.strip() for e in raw_address if e.strip()]
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if street_address == "100":
            street_address = loc_dom.xpath(
                '//h3[contains(text(), "Address:")]/following-sibling::p[1]/text()'
            )[0]
        city = addr.city
        if not city:
            city = location_name.replace("Outlet", "")
        phone = loc_dom.xpath('//a[contains(@onclick, "tel")]/text()')[0]
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2m3")[0]
            .split("!3d")
        )
        hoo = loc_dom.xpath('//div[@class="storeLanding-info-hours-list"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="AU",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1],
            longitude=geo[0],
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
