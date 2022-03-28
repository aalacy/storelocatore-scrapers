import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.dia.com.br/page-data/index/page-data.json"
    domain = "dia.com.br"
    data = session.get(start_url).json()

    for poi in data["result"]["data"]["lojas"]["nodes"]:
        page_url = "https://www.dia.com.br/lojas/" + poi["slug"]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath('//li[contains(@class, "footer-module--phone")]/text()')[
            0
        ]
        hoo = (
            loc_dom.xpath('//p[contains(text(), "Nosso horário de")]/text()')[-1]
            .split("atendimento é")[-1][:-1]
            .strip()
        )
        latitude = poi["lat"]
        if latitude == 0:
            latitude = ""
        longitude = poi["lng"]
        if longitude == 0:
            longitude = ""
        poi_data = loc_dom.xpath('//script[contains(text(), "address")]/text()')[0]
        poi_data = json.loads(poi_data)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"],
            city=poi["city"],
            state=poi["district"],
            zip_postal=poi["cep"],
            country_code="BR",
            store_number=poi["storeNumber"],
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
