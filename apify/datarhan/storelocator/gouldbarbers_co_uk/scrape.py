# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.gouldbarbers.co.uk/locations"
    domain = "gouldbarbers.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_coordinates = dom.xpath("//@data-markers")[0].split("|")
    all_names = dom.xpath("//@data-names")[0].split("|")
    all_phones = dom.xpath("//@data-phones")[0].split("|")
    all_addresses = dom.xpath("//@data-addresses")[0].split("|")
    all_urls = dom.xpath("//@data-pageurls")[0].split("|")

    for i, page_url in enumerate(all_urls):
        raw_address = " ".join(all_addresses[i].replace("<br />", "").split())
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        days = loc_dom.xpath(
            '//p[contains(text(), "Times")]/following-sibling::div[1]/div[1]//text()'
        )
        days = [e.strip() for e in days if e.strip()]
        hours = loc_dom.xpath(
            '//p[contains(text(), "Times")]/following-sibling::div[1]/div[2]//text()'
        )
        hours = [e.strip() for e in hours if e.strip()]
        hoo = ", ".join(list(map(lambda d, h: d + " " + h, days, hours)))

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=all_names[i],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=all_phones[i],
            location_type="",
            latitude=all_coordinates[i].split(", ")[0],
            longitude=all_coordinates[i].split(", ")[-1],
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
