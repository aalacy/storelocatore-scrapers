# -*- coding: utf-8 -*-
import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://stores.petco.com/"
    domain = "petco.com/unleashed"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//a[@class="gaq-link"]/@href')
    for url in all_states:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_cities = dom.xpath(
            '//div[@class="map-list-item-wrap is-single"]//a[@class="gaq-link"]/@href'
        )
        for url in all_cities:
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//div[@data-brand="Unleashed"]/a/@href')

            for page_url in all_locations:
                loc_response = session.get(page_url)
                loc_dom = etree.HTML(loc_response.text)

                poi = loc_dom.xpath('//script[@id="indy-schema"]/text()')[0]
                poi = json.loads(poi)[0]
                location_name = (
                    poi["name"]
                    .replace("Welcome to your Unleashed in ", "")
                    .replace("Welcome to your ", "")
                    .replace("!", "")
                    .strip()
                )
                store_number = re.findall(r"-(\d+).html", str(loc_response.url))[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=poi["address"]["streetAddress"],
                    city=poi["address"]["addressLocality"],
                    state=poi["address"]["addressRegion"],
                    zip_postal=poi["address"]["postalCode"],
                    country_code="",
                    store_number=store_number,
                    phone=poi["address"]["telephone"],
                    location_type=poi["@type"],
                    latitude=poi["geo"]["latitude"],
                    longitude=poi["geo"]["longitude"],
                    hours_of_operation=poi["openingHours"],
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
