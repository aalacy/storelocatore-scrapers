# -*- coding: utf-8 -*-
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()

    start_url = "https://www.walmartchile.cl/contenidos/locales/"
    url = "https://www.walmartchile.cl/wp-admin/admin-ajax.php"
    domain = "walmartchile.cl"
    hdr = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
    nonce = dom.xpath('//input[@name="nonce"]/@value')[0]
    data = (
        dom.xpath('//script[contains(text(), "data =")]/text()')[0]
        .split("data =")[-1]
        .split(";;\n\tjQuery")[0]
    )
    data = json.loads(data)
    for r in data["regiones"]:
        for c in r["comunas"]:
            frm = f'action=obtener_locales&nonce={nonce}&supermercados%5B%5D=lider&supermercados%5B%5D=express&supermercados%5B%5D=acuenta&supermercados%5B%5D=ekono&supermercados%5B%5D=mayorista&region={r["id"]}&comuna={c["id"]}'
            response = session.post(url, data=frm, headers=hdr)
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//div[@class="local"]')
            for poi_html in all_locations:
                location_type = poi_html.xpath('.//div[@class="info"]/span/text()')[0]
                location_name = poi_html.xpath('.//div[@class="info"]/h3/text()')[0]
                street_address = poi_html.xpath('.//div[@class="info"]/p/text()')[0]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=start_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=c["name"],
                    state=r["name"],
                    zip_postal="",
                    country_code="CL",
                    store_number="",
                    phone="",
                    location_type=location_type,
                    latitude="",
                    longitude="",
                    hours_of_operation="",
                )

                yield item

        frm = f'action=obtener_locales&nonce={nonce}&supermercados%5B%5D=lider&supermercados%5B%5D=express&supermercados%5B%5D=acuenta&supermercados%5B%5D=ekono&supermercados%5B%5D=mayorista&region={r["id"]}&comuna=00000'
        response = session.post(url, data=frm, headers=hdr)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="local"]')
        for poi_html in all_locations:
            location_type = poi_html.xpath('.//div[@class="info"]/span/text()')[0]
            street_address = poi_html.xpath('.//div[@class="info"]/p/text()')[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_type,
                street_address=street_address,
                city="",
                state=r["name"],
                zip_postal="",
                country_code="CL",
                store_number="",
                phone="",
                location_type=location_type,
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
