# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.walmartmexico.com/conocenos/directorio-de-tiendas"
    domain = "walmartmexico.com"

    response = session.post(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//tbody[@class="MapModuleFilterable-table-items"]/tr')
    load_more = dom.xpath('//a[@data-loadmorelabel="Carga más"]/@href')
    while load_more:
        response = session.get(urljoin(start_url, load_more[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//tbody[@class="MapModuleFilterable-table-items"]/tr'
        )
        load_more = dom.xpath('//a[@data-loadmorelabel="Carga más"]/@href')

    for poi_html in all_locations:
        raw_data = poi_html.xpath(".//td/text()")
        if len(raw_data) == 3:
            raw_data.insert(0, "")

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.walmartmexico.com/conocenos/directorio-de-tiendas",
            location_name=raw_data[0],
            street_address=raw_data[1],
            city=raw_data[2],
            state=raw_data[3],
            zip_postal="",
            country_code="",
            store_number="",
            phone="",
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
