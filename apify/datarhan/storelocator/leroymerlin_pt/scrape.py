# -*- coding: utf-8 -*-
import json
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
    start_url = "https://www.leroymerlin.pt/pt/lojas"
    domain = "leroymerlin.pt"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "allStores")]/text()')[0]
        .split("allStores = ")[1]
        .split("var cards")[0]
        .strip()[:-1]
    )
    all_locations = json.loads(data)
    for poi in all_locations.values():
        page_url = urljoin(start_url, poi["url"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath(
            '//div[contains(text(), "LOJA")]/following-sibling::div[1]/p/text()'
        )[:2]
        if not raw_address:
            continue
        raw_address = " ".join(" ".join(raw_address).split())
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = loc_dom.xpath(
            '//div[contains(text(), "LOJA")]/following-sibling::div[1]/p[contains(text(), "Segunda")]/text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        latitude = poi["loja_latitude"]
        if latitude.startswith("."):
            latitude = latitude[1:]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["loja_name"],
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="PT",
            store_number=poi["page_id"],
            phone=poi["loja_phone"],
            location_type="",
            latitude=latitude,
            longitude=poi["loja_longitude"],
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
