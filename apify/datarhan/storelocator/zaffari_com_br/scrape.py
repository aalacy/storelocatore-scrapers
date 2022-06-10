# -*- coding: utf-8 -*-
from lxml import etree

from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    start_url = "https://www.zaffari.com.br/lojas/"
    domain = "zaffari.com.br"
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[contains(@class, "lista-lojas-individual")]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_address = poi_html.xpath(
            './/div[@class="lista-lojas-class-replace"]/p[1]/span/text()'
        )[0]
        phone = poi_html.xpath('.//li[@class="buscaLojasFone"]/text()')[0]
        hoo = poi_html.xpath(
            './/li[strong[contains(text(), "Horário de Atendimento:")]]/text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address.split(" - ")[0],
            city=raw_address.split(" - ")[-1].split("/")[0],
            state=raw_address.split(" - ")[-1].split("/")[-1],
            zip_postal="",
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
