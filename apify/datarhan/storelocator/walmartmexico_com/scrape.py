# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.walmartmexico.com/_ajax/getStores"
    domain = "walmartmexico.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    frm = {
        "ajaxMainObjectId": "00000157-910b-de9b-adf7-d17f1cc80000",
        "offset": "0",
        "count": "10",
    }
    response = session.post(start_url, headers=hdr, data=frm)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@id="store-information"]/table/tr')
    load_more = dom.xpath('//button[contains(text(), "Cargar")]')
    while load_more:
        offset = load_more[0].xpath("@data-offset")[0]
        frm["offset"] = offset
        response = session.post(start_url, headers=hdr, data=frm)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@id="store-information"]/table/tr')
        load_more = dom.xpath('//button[contains(text(), "Cargar")]')

    for poi_html in all_locations:
        location_name = poi_html.xpath("./td[1]/text()")[-1].strip()
        store_number = poi_html.xpath("./td[1]/text()")[0].strip()[1:]
        raw_data = poi_html.xpath("./td[2]/text()")
        raw_data = [e.replace("\xa0", " ").strip() for e in raw_data if e.strip()]
        street_address = raw_data[0]
        addr = parse_address_intl(", ".join(raw_data[1:]))
        city = poi_html.xpath('.//td[@data-colname="City"]/text()')
        city = city[0] if city else ""
        if not city:
            city = addr.city
        state = poi_html.xpath('.//td[@data-colname="State"]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.walmartmexico.com/conocenos/directorio-de-tiendas",
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=addr.postcode,
            country_code=raw_data[-1],
            store_number=store_number,
            phone="",
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address=", ".join(raw_data),
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
