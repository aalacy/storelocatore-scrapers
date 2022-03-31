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

    start_url = "https://www.zodio.fr/trouver-un-magasin/"
    domain = "zodio.fr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="zo-store-locator__store-list"]/li/a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')
        if poi:
            poi = json.loads(
                poi[0]
                .replace("\n", "")
                .replace("\r", " ")
                .replace('"Buld', "Buld")
                .replace('Centre"', "Centre")
            )
            location_name = poi["location"]["name"]
            street_address = poi["location"]["address"]["streetAddress"]
            city = poi["location"]["address"]["addressLocality"]
            zip_code = poi["location"]["address"]["postalCode"]
            country_code = poi["location"]["address"]["addressCountry"]
            raw_address = ""
        else:
            location_name = loc_dom.xpath('//h1[@class="zo-store__title"]/text()')[
                0
            ].split("magasin")[-1]
            raw_data = loc_dom.xpath(
                '//p[@class="zo-store__practical-infos-contact"]/text()'
            )
            raw_data = [e.strip() for e in raw_data if e.strip()]
            raw_address = ", ".join(raw_data[:2]).replace("r5", "r 5")
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            city = addr.city
            zip_code = addr.postcode
            country_code = "France"
        phone = loc_dom.xpath(
            '//p[@class="zo-store__practical-infos-contact" and svg[use]]/text()'
        )[-1]
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Horaires")]/following-sibling::ul//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        hoo = " ".join(hoo.split())

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number=page_url.split("-")[-1][:-1],
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
