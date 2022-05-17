# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://www.adecco.hr/kontakti/",
        "https://www.adecco.hr/kontakti/adecco-pula/",
        "https://www.adecco.hr/kontakti/adecco-rijeka/",
    ]
    domain = "adecco.hr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for page_url in start_urls:
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath('//h1[@class="h2"]/text()')[0]
        raw_address = loc_dom.xpath('//div[@class="contact-block"]/ul/li/text()')[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        zip_code = addr.postcode
        if "10 000" in street_address:
            street_address = street_address.replace("10 000", "")
            zip_code = "10 000"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        if not phone:
            phone = loc_dom.xpath('//li[contains(text(), "Mobitel:")]/text()')
        phone = phone[0].split("Mobitel:")[-1] if phone else ""
        latitude = re.findall('lat":"(.+?)",', loc_response.text)[0]
        longitude = re.findall('lng":"(.+?)"', loc_response.text)[0]
        hoo = (
            loc_dom.xpath('//li[contains(text(), "Radno vrijeme")]/text()')[0]
            .split("vrijeme:")[-1]
            .strip()
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code="HR",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
