# -*- coding: utf-8 -*-
import ssl
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def fetch_data():
    session = SgRequests()

    start_url = "https://www.gocco.es/tiendas-gocco"
    domain = "gocco.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="results striped stores-list__section"]/div'
    )
    for poi_html in all_locations:
        store_number = poi_html.xpath(".//@data-store-id")[0]
        latitude = poi_html.xpath(".//@data-lat")[0]
        longitude = poi_html.xpath(".//@data-lon")[0]

        location_name = poi_html.xpath('.//a[@class="store-map"]/text()')[0]
        raw_address = poi_html.xpath(".//address/div/text()")
        raw_address = [e.strip() for e in raw_address if e.strip() and "TLF" not in e]
        raw_address = [e for e in raw_address if "entrada por" not in e]
        phone = poi_html.xpath('.//a[@class="storelocator-phone"]/text()')
        phone = phone[0] if phone else ""
        location_type = ""
        if "El Corte Ingles" in location_name:
            location_type = "El Corte Ingles"
        hoo = poi_html.xpath('.//div[@class="store-hours"]//text()')
        hoo = " ".join(
            [
                e.replace("Horario:", "").replace("\n", "").strip()
                for e in hoo
                if e.strip()
            ]
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split("\n")[1],
            state="",
            zip_postal=raw_address[1].split("\n")[0],
            country_code=raw_address[2],
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
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
