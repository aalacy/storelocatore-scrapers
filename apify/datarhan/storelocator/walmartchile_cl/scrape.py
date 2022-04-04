# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.walmartchile.cl/contenidos/locales/"
    domain = "walmartchile.cl"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "data =")]/text()')[0]
        .split("data =")[-1]
        .split(";;\n\tjQuery")[0]
    )
    data = json.loads(data)
    nonce = dom.xpath('//input[@name="nonce"]/@value')[0]
    for r in data["regiones"]:
        for c in r["comunas"]:
            url = "https://www.walmartchile.cl/wp-admin/admin-ajax.php"
            frm = f'action=obtener_locales&nonce=42d83027dc&supermercados%5B%5D=lider&supermercados%5B%5D=express&supermercados%5B%5D=acuenta&supermercados%5B%5D=ekono&supermercados%5B%5D=mayorista&region={r["id"]}&comuna={c["id"]}'
            hdr = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Host": "www.walmartchile.cl",
                "Origin": "https://www.walmartchile.cl",
                "Pragma": "no-cache",
                "Referer": "https://www.walmartchile.cl/contenidos/locales/",
                "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
            }
            response = session.post(url, data=frm, headers=hdr)
            dom = etree.HTML(response.text)
            all_locations = dom.xpath('//div[@class="local"]')
            for poi_html in all_locations:
                location_type = poi_html.xpath('//div[@class="info"]/span/text()')[0]
                location_name = dom.xpath('//div[@class="info"]/h3/text()')[0]
                street_address = dom.xpath('//div[@class="info"]/p/text()')[0]

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
