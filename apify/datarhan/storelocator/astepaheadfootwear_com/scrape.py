# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.astepaheadfootwear.com/service/store-locations/"
    domain = "astepaheadfootwear.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//main/section")
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2//text()")[0]
        street_address = poi_html.xpath('.//div[@class="editor"]/p[1]//text()')[
            0
        ].replace("\xa0", " ")
        if street_address.startswith("Mon"):
            street_address = ""
        hoo = poi_html.xpath('.//*[contains(text(), "pm")]/text()')
        hoo = " ".join([e.strip() for e in hoo])
        raw_data = poi_html.xpath('.//div[@class="editor"]/p[4]//text()')
        if raw_data and not raw_data[0].strip():
            raw_data = ""
        if not raw_data:
            raw_data = poi_html.xpath('.//div[@class="editor"]/p[2]/text()')
        if raw_data and "Telephone" in raw_data[0]:
            raw_data = poi_html.xpath('.//div[@class="editor"]/p[1]/text()')
        raw_data = raw_data[0].replace("\xa0", " ")
        city = raw_data.split(", ")[0]
        if street_address.startswith(city):
            street_address = ""
        state = raw_data.split(", ")[-1].split()[0]
        country_code = raw_data.split(", ")[-1].split()[1]
        zip_code = " ".join(raw_data.split(", ")[-1].split()[2:])
        phone = poi_html.xpath(
            './/div[@class="editor"]/p[contains(text(), "Telephone")]/text()'
        )[0].split(": ")[-1]
        geo = poi_html.xpath(".//a/@href")[0].split("/@")[-1].split(",")[:2]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
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
