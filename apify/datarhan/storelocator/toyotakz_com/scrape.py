# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyotakz.com/dealers/toyota-dealers"
    domain = "toyotakz.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@data-gt-name="dealerevent"]/div/div')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        if "Тойота Сервис" in location_name:
            continue
        raw_address = poi_html.xpath('.//li[@class="address"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()][0]
        street_address = raw_address.split(" - ")[0]
        if street_address.startswith("г."):
            city = street_address.split(", ")[0].replace("г.", "")
            street_address = ", ".join(street_address.split(", ")[1:])
        phone = poi_html.xpath('.//a[@data-gt-action="call-dealer"]/text()')[0]
        zip_code = poi_html.xpath(".//@data-gt-dealerzipcode")[0]
        if zip_code == "-":
            zip_code = ""
        state = poi_html.xpath(".//@data-gt-dealerregion")
        state = state[0] if state else ""
        city = poi_html.xpath(".//@data-gt-dealercity")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="KZ",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
