import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.grandhomefurnishings.com/store-locations"
    domain = "grandhomefurnishings.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "More Information")]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')
        if not poi:
            continue
        poi = json.loads(poi[0])
        hoo = loc_dom.xpath('//div[@id="location-hours"]//li//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["address"]["streetAddress"],
            city=poi["address"]["addressLocality"],
            state=poi["address"]["addressRegion"],
            zip_postal=poi["address"]["postalCode"],
            country_code="",
            store_number="",
            phone=poi["telephone"],
            location_type=poi["@type"],
            latitude=poi["geo"]["latitude"],
            longitude=poi["geo"]["longitude"],
            hours_of_operation=hoo,
        )

        yield item

    response = session.get(
        "https://www.grandhomefurnishings.com/store-locations/warehouses"
    )
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="warehouse-info-row"]')
    for poi_html in all_locations:
        raw_data = poi_html.xpath(
            './/div[@class="warehouse-info location-page-block"]/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        location_name = " ".join(raw_data[1].split()[:-1])
        hoo = poi_html.xpath("./div[2]//text()")
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.grandhomefurnishings.com/store-locations/warehouses",
            location_name=location_name,
            street_address=raw_data[0],
            city=location_name.split(", ")[0],
            state=location_name.split(", ")[-1],
            zip_postal=raw_data[1].split()[-1],
            country_code="",
            store_number="",
            phone=raw_data[-1],
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
