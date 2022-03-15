import json
import datetime
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "footsolutions.com"
    start_url = "https://footsolutions.com/locations/"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "FWP_JSON =")]/text()')[0]
        .split("JSON =")[-1]
        .split(";\nwindow.FWP_HTTP")[0]
    )
    data = json.loads(data)
    all_locations = data["preload_data"]["settings"]["map"]["locations"]
    for poi in all_locations:
        poi_html = etree.HTML(poi["content"])
        page_url = poi_html.xpath("//a/@href")[0]
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath("//strong/text()")[0]
        raw_address = poi_html.xpath('//div[@class="address"]//text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if len(raw_address) == 3:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        phone = loc_dom.xpath('//a[@class="phone"]/span/text()')[0]
        hoo = loc_dom.xpath('//div[@class="hours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)
        today = datetime.datetime.today().strftime("%A")
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow = tomorrow.strftime("%A")
        hoo = hoo.replace("Today", today).replace("Tomorrow", tomorrow)
        zip_code = " ".join(raw_address[1].split(", ")[-1].split()[1:])
        country_code = "US"
        if len(zip_code.split()) == 2:
            country_code = "CA"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1].split()[0],
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude=poi["position"]["lat"],
            longitude=poi["position"]["lng"],
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
