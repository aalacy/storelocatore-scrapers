import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(proxy_country="us")
    domain = "melrosestore.com"
    start_url = "https://melrosestore.com/store-locator/"
    response = session.get(start_url)
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "amLocator")]/text()')[0]
    data = re.findall(r"amLocator\((.+)\);", data.replace("\n", ""))[0]
    data = demjson.decode(data.split(");")[0])

    for poi in data["jsonLocations"]["items"]:
        poi_html = etree.HTML(poi["popup_html"])
        store_url = poi_html.xpath('//a[@class="amlocator-link"]/@href')[0]
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        raw_data = poi_html.xpath("//div/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        location_name = poi_html.xpath('//a[@class="amlocator-link"]/text()')[0]
        store_number = poi["id"]
        phone = raw_data[-1]
        location_type = ""
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = loc_dom.xpath('//div[@class="amlocator-schedule-table"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=raw_data[1],
            city=raw_data[2].split(", ")[0],
            state=" ".join(raw_data[2].split(", ")[-1].split()[:-1]),
            zip_postal=raw_data[2].split(", ")[-1].split()[-1],
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type=location_type,
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
