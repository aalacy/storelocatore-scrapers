import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "evereve.com"
    start_url = "https://evereve.com/amlocator/index/ajax/"
    formdata = {
        "lat": "",
        "lng": "",
        "radius": "",
        "mapId": "amlocator-map-canvas5fef59650b3e7",
        "storeListId": "amlocator_store_list5fef596505523",
        "product": "0",
        "category": "0",
        "sortByDistance": "1",
        "p": "ajax",
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["items"]:
        poi_html = etree.HTML(poi["popup_html"])
        page_url = poi_html.xpath('//a[@class="amlocator-link"]/@href')[0]
        location_name = poi_html.xpath('//a[@class="amlocator-link"]/text()')[0]
        if "Coming Soon" in location_name:
            continue
        street_address = poi_html.xpath("//div/text()")[1]
        zip_code = poi_html.xpath("//div/text()")[2].split()[-1]
        raw_address = poi_html.xpath("//div/text()")[2]
        addr = parse_address_intl(raw_address)
        city = addr.city
        state = addr.state
        phone = poi_html.xpath("//div/text()")[-2]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[@class="amlocator-schedule-table"]//span/text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=poi["id"],
            phone=phone,
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
