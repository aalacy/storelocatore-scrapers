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

    start_url = "https://www.tonyromas.es/restaurantes-resultado/"
    domain = "tonyromas.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_regions = dom.xpath('//select[@name="localidad"]/option/@value')
    all_regions = [e for e in all_regions if e != "#"]
    for e in all_regions:
        page_url = (
            f"https://www.tonyromas.es/restaurantes-resultado/?nogames=&localidad={e}"
        )
        response = session.get(page_url)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//div[@class="bloque-restaurante"]')
        for poi_html in all_locations:
            location_name = poi_html.xpath(".//h2/text()")[0]
            raw_address = poi_html.xpath(".//p[1]/text()")
            street_address = ""
            city = ""
            state = dom.xpath('//option[@value="{}"]/text()'.format(e))[0].replace(
                "--", ""
            )
            zip_code = ""
            phone = ""
            if raw_address:
                raw_address = raw_address[0]
                if ":" in raw_address:
                    phone = raw_address.split(":")[-1]
                    if "," in phone:
                        phone = ""
                raw_address = (
                    raw_address.split("Tlf")[0]
                    .split("Teléf")[0]
                    .split("Telf")[0]
                    .split("telf:")[0]
                )
                raw_address = " ".join(raw_address.split())
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2
                city = addr.city
                if city and city.endswith("."):
                    city = city[:-1]
                zip_code = addr.postcode
            if not raw_address:
                raw_address = ""
            hoo = " ".join(
                " ".join(poi_html.xpath('.//p[@class="horarios"]/text()')).split()
            )

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="ES",
                store_number="",
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
