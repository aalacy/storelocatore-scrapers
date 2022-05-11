# -*- coding: utf-8 -*-
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
    domain = "adeg.at"
    start_url = "https://www.adeg.at"
    for i in range(1, 100):
        url = f"https://www.adeg.at/karriere/unsere-kaufleute/adeg-kaufleute?tx_solr[page]={i}&type=7382"
        data = session.get(url).json()
        dom = etree.HTML(data["htmlList"])
        if not dom:
            break
        all_locations = dom.xpath('//li[@class="merchant"]')
        for poi_html in all_locations:
            location_name = poi_html.xpath(".//h3/a/text()")[0]
            url = poi_html.xpath(".//h3/a/@href")[0]
            page_url = urljoin(start_url, url)
            raw_address = poi_html.xpath(".//address/div/text()")
            raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
            phone = phone[0] if phone else ""
            hoo = poi_html.xpath('.//dl[@class="opening-hours"]//text()')
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="AT",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.PAGE_URL})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
