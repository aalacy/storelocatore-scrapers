# -*- coding: utf-8 -*-
import re
import demjson
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://renault.com.do/servicios/Geolocalizador.html"
    domain = "renault.com.do"

    with SgFirefox() as driver:
        driver.get(start_url)
        driver.switch_to.frame(driver.find_element_by_id("sectionIframe"))
        dom = etree.HTML(driver.page_source)
    all_geo = re.findall(r"renault = (\{.+?\})\;", str(etree.tostring(dom)))

    all_locations = dom.xpath(
        '//a[@class="list-group-item list-group-item-action flex-column align-items-start"]'
    )
    for i, poi_html in enumerate(all_locations):
        location_name = poi_html.xpath(".//h5/b/text()")[0]
        street_address = poi_html.xpath('.//p[@class="mb-1"]/text()')[0]
        phone = poi_html.xpath('.//p[b[contains(text(), "Telefonos:")]]/text()')[
            0
        ].split("/")[0]
        hoo = poi_html.xpath('.//p[b[contains(text(), "Horario:")]]/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        geo = demjson.decode(all_geo[i])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=location_name.replace("RENAULT", ""),
            state="",
            zip_postal="",
            country_code="DO",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo["lat"],
            longitude=geo["lng"],
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
