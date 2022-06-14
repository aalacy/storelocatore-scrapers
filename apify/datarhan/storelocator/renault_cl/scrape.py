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

    start_url = "https://www.renault.cl/concesionarios/"
    domain = "renault.cl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    session.get(
        "https://www.renault.cl/concesionarios/rm-region-metropolitana-de-santiago/todos/venta",
        headers=hdr,
    )
    data = session.get(
        "https://middleware.dercocenter.cl/api/jsons/v4/subsidiaries/filters",
        headers=hdr,
    ).json()
    for r in data["filters"]["regions"]:
        url = start_url + r["slug"]
        response = session.get(url, headers=hdr)
        if response.status_code != 200:
            continue
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//div[@class="subsidiaries-list-container"]/div/div')
        for poi_html in all_locations:
            location_name = poi_html.xpath(".//h4/text()")[0]
            addr = parse_address_intl(location_name)
            street_address = poi_html.xpath(
                './/div[@class="subsidiary-card-header"]/p[1]/text()'
            )[0]
            geo = (
                poi_html.xpath(".//a[contains(@href, 'maps')]/@href")[0]
                .split("/")[-1]
                .split(",")
            )
            hoo = poi_html.xpath(
                './/h5[contains(text(), "Venta")]/following-sibling::div[1]/ul[1]/li//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            phone = poi_html.xpath('.//a[@class="contact-number-link"]/text()')
            phone = phone[0] if phone else ""
            if phone and phone == "null":
                phone = ""
            types = poi_html.xpath(
                './/div[@class="subsidiary-card-body"]/ul/li/h5/text()'
            )
            location_type = ", ".join([e.strip() for e in types if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=r["name"],
                zip_postal="",
                country_code="CL",
                store_number="",
                phone=phone,
                location_type=location_type,
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
