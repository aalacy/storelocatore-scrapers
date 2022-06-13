# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.drycleanusa.com.br/nossas-lojas"
    domain = "drycleanusa.com.br"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//select[@id="estado"]/option/@value')
    for state in all_states:
        frm = {"estado": state}
        response = session.post(
            "https://www.drycleanusa.com.br/index/load-cidades", data=frm
        )
        dom = etree.HTML(response.text)
        all_cities = dom.xpath("//option/@value")
        for city in all_cities:
            frm = {
                "latitude": "",
                "longitude": "",
                "estado": state,
                "cidade": city,
                "cep": "",
                "page": "nossas-lojas",
            }
            response = session.post(
                "https://www.drycleanusa.com.br/index/get-franquia", data=frm
            )
            dom = etree.HTML(response.text)

            all_locations = dom.xpath('//div[@class="franquia"]')
            for poi_html in all_locations:
                location_name = poi_html.xpath('.//h3[@class="nome"]/text()')[0]
                street_address = poi_html.xpath('.//p[@class="rua-numero"]/text()')[0]
                if not street_address.replace(",", "").strip():
                    street_address = ""
                city = (
                    poi_html.xpath('.//p[@class="bairro-cidade-uf"]/text()')[0]
                    .split(" - ")[1]
                    .split("/")[0]
                )
                phone = poi_html.xpath(
                    './/a[@class="wp telefone click_telefone"]/text()'
                )
                phone = phone[-1].strip() if phone else ""
                geo_url = poi_html.xpath('.//div[@class="mapa"]/iframe/@src')[0]
                response = session.get(geo_url)
                if "Brasil" in response.text:
                    geo = response.text.split('Brasil",[')[1].split("]]")[0].split(",")
                else:
                    try:
                        geo = re.findall(r",\[null,null,(-.+?)\]", response.text)[
                            0
                        ].split(",")
                    except Exception:
                        geo = re.findall(r",(-.+?)\]", response.text)[0].split(",")

                item = SgRecord(
                    locator_domain=domain,
                    page_url=start_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal="",
                    country_code="BR",
                    store_number="",
                    phone=phone,
                    location_type="",
                    latitude=geo[0],
                    longitude=geo[1],
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
