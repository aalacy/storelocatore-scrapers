# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://columbiasportswear.com.ar/donde-comprar"
    domain = "columbiasportswear.com.ar"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text.replace("<!--", "").replace("-->", ""))

    all_locations = dom.xpath('//p[@class="nombre"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath("text()")[0]
        street_address = poi_html.xpath(
            './/following-sibling::p[@class="direccion"][1]/text()'
        )[0]
        city = poi_html.xpath(
            './/preceding-sibling::p[@class="titulo-ciudad"][1]/text()'
        )[0]
        phone = poi_html.xpath('.//following-sibling::p[@class="telefono"][1]/text()')[
            0
        ]
        hoo = poi_html.xpath('.//following-sibling::p[@class="horario"][1]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="AR",
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
