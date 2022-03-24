# -*- coding: utf-8 -*-
from lxml import etree
from time import sleep

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    start_url = "https://www.cimaco.com.mx/sucursales"
    domain = "cimaco.com.mx"

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(15)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="suc-post"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_data = poi_html.xpath("./p[1]/text()")
        if len(raw_data) == 3:
            raw_address = raw_data[0] + ", " + raw_data[2]
        elif len(raw_data) == 2:
            raw_address = raw_data[0].split("Tel.")[0] + ", " + raw_data[1]
        else:
            raw_address = (
                raw_data[0].split("Tel.")[0]
                + " "
                + " ".join(raw_data[0].split("Tel.")[-1].split()[2:])
            )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        geo = poi_html.xpath('.//a[contains(@href, "maps")]/@href')
        latitude = ""
        longitude = ""
        if geo:
            if "ll=" in geo[0]:
                geo = geo[0].split("ll=")[-1].split("&")[0].split(",")
                latitude = geo[0]
                longitude = geo[1]
            if "q=" in geo[0]:
                geo = geo[0].split("q=")[-1].split("&")[0].split(",")
                latitude = geo[0]
                longitude = geo[1]
        if len(raw_data) == 3:
            phone = raw_data[1]
        else:
            phone = " ".join(raw_data[0].split("Tel.")[-1].split()[:2])
        phone = phone.replace("Tel. ", "")
        city = addr.city.replace(".", "")

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state.replace(".", ""),
            zip_postal=addr.postcode.replace("C.P.", "").replace("CP", ""),
            country_code="MX",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation="",
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
