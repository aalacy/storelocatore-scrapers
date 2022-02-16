# -*- coding: utf-8 -*-
import ssl
import json
from lxml import etree
from urllib.parse import urljoin
from time import sleep

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgChrome

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    session = SgRequests()

    start_url = "https://www.heb.com/store-locations"
    domain = "heb.com"
    with SgChrome() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[@class="store-card__action"]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        pharmacy = loc_dom.xpath('//h2[contains(text(), "Pharmacy")]')
        if not pharmacy:
            continue
        poi = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')[0]
        poi = json.loads(poi)
        poi = poi["department"][0]
        hoo = []
        for e in poi["openingHoursSpecification"]:
            hoo.append(f'{e["dayOfWeek"]}: {e["opens"]} - {e["closes"]}')
        hoo = " ".join(hoo)
        geo = (
            loc_dom.xpath("//source/@srcset")[0]
            .split("?center=")[-1]
            .split("&")[0]
            .split("%2C")
        )
        if len(geo) == 1:
            geo = ["", ""]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=poi["address"]["postalCode"],
            country_code=poi["address"]["addressCountry"],
            store_number="",
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
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
