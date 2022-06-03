# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.alimerka.es/area-cliente/localizador-de-supermercados/"
    domain = "alimerka.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@id="localizador"]/div')
    url = "https://www.alimerka.es/localizador-de-supermercados/?_sft_localidad={}"
    all_cities = dom.xpath('//select[@class="sf-input-select"]/option/@value')
    for c in all_cities:
        response = session.get(url.format(c))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@id="localizador"]/div')

    for poi_html in all_locations:
        location_name = poi_html.xpath('.//div[@class="h2"]/text()')[0]
        street_address = poi_html.xpath(".//div[2]/text()")[0]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        raw_data = poi_html.xpath("./div[4]/text()")
        city = location_name.split("–")[0]
        zip_code = ""
        if raw_data:
            raw_data = raw_data[0].split()
            city = " ".join(raw_data[1:])
            zip_code = raw_data[0]
        geo = poi_html.xpath('.//div[@class="gmaps"]//a/@href')[0]
        latitude = ""
        longitude = ""
        if "@" in geo:
            geo = geo.split("@")[1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]

        hoo = (
            poi_html.xpath('.//div[contains(text(), " horas")]/text()')[0]
            .split("Horario:")[-1]
            .strip()
        )

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.alimerka.es/localizador-de-supermercados",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="ES",
            store_number="",
            phone=phone,
            location_type="",
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
