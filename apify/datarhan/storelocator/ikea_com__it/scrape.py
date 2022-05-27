# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com/it/it/stores/"
    domain = "ikea.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//h2[contains(text(), "Orari negozi IKEA")]/following-sibling::p/a/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        hoo = loc_dom.xpath(
            '//h3[contains(text(), "apertura negozio")]/following-sibling::p/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h2[contains(text(), "Negozio")]/following-sibling::dl//text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[contains(text(), "Orari d")]/following-sibling::p/text()'
            )
        hoo = " ".join([e.strip() for e in hoo if e.strip()]).split(": 25")[0]
        poi = loc_dom.xpath('//div[@data-pub-type="store"]/script/text()')
        latitude = ""
        longitude = ""
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            zip_code = poi["address"]["postalCode"]
            country_code = poi["address"]["addressCountry"]
            location_type = poi["@type"]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
            raw_adr = ""
        else:
            location_name = loc_dom.xpath("//h1/text()")[0]
            raw_adr = loc_dom.xpath(
                '//*[contains(text(), "Indirizzo")]/following-sibling::p/text()'
            )
            if not raw_adr:
                raw_adr = loc_dom.xpath(
                    '//h3[contains(text(), "Dove siamo")]/following-sibling::p[1]/text()'
                )
            raw_adr = [e.strip() for e in raw_adr if e.strip() and "Google" not in e]
            raw_adr = " ".join(" ".join(raw_adr).split())
            addr = parse_address_intl(raw_adr)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            zip_code = addr.postcode
            country_code = addr.country
            location_type = ""

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
            phone="",
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=raw_adr,
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
