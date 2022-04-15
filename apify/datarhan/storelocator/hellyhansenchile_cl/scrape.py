# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.hellyhansenchile.cl/locales"
    domain = "hellyhansenchile.cl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//div[@class="col-md-10"]//div[@class="col-md-4"]')
    for c_html in all_cities:
        all_locations = c_html.xpath(
            './/strong[not(@style) and not(contains(text(), "Fono")) and not(contains(text(), "Horario"))]'
        )
        for poi_html in all_locations:
            location_name = poi_html.xpath("text()")[0]
            street_address = poi_html.xpath(".//following::text()")[0]
            city = c_html.xpath(".//h4/text()")[0]
            phone = poi_html.xpath(".//following-sibling::strong[1]/text()")[0]
            phone = phone.split(":")[-1] if "Fono" in phone else ""
            hoo = poi_html.xpath(".//following-sibling::strong[2]/text()")
            hoo = (
                " ".join(hoo).split("Horario:")[-1]
                if hoo and "Horario" in hoo[0]
                else ""
            )
            if not hoo:
                hoo = poi_html.xpath(".//following-sibling::strong[1]/text()")
                hoo = (
                    " ".join(hoo).split("Horario:")[-1]
                    if hoo and "Horario" in hoo[0]
                    else ""
                )
            hoo = hoo.replace("(", "").replace(")", "").split("*")[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
                zip_postal="",
                country_code="CL",
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
