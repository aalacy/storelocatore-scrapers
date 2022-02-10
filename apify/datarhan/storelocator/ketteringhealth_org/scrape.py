import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "ketteringhealth.org"
    start_url = "https://ketteringhealth.org/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "FWP_JSON")]/text()')[0]
        .split(";\nwindow")[0]
        .split("FWP_JSON =")[-1]
    )
    data = json.loads(data)

    for poi in data["preload_data"]["settings"]["map"]["locations"]:
        poi_html = etree.HTML(poi["content"])
        page_url = poi_html.xpath(".//a/@href")[0]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//strong/text()")[0]
        if "Coming Soon" in location_name:
            continue
        raw_address = poi_html.xpath('.//div[@class="address"]/text()')
        raw_address = [e.strip() for e in raw_address]
        if len(raw_address) == 3:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        phone = loc_dom.xpath('//span[@class="phone-number"]/text()')
        if not phone:
            phone = loc_dom.xpath(
                '//div[@class="profile-content"]//a[contains(@href, "tel")]/@href'
            )
        phone = phone[0].split(":")[-1] if phone else ""
        hoo = loc_dom.xpath(
            '//div[@class="profile-content"]//ul[@class="hours-list"]/li/div/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath('//div[@class="hours-info"]//span/text()')
        hoo = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[-1].split()[0],
            zip_postal=raw_address[1].split(", ")[-1].split()[-1],
            country_code="",
            store_number=poi["post_id"],
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
