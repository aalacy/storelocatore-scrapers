import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.ro/contact/dealers/list"
    domain = "lexus.ro"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="dealer-details"]')
    for poi_html in all_locations:
        page_url = poi_html.xpath('.//a[@data-gt-action="view-dealer"]/@href')[0]
        page_url = urljoin(start_url, page_url)
        phone = poi_html.xpath('.//a[@data-gt-action="call-dealer"]/text()')
        phone = phone[0].split(",")[0].split("/")[0] if phone else ""
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_address = poi_html.xpath('.//li[@class="address"]/text()')[0]
        zip_code = poi_html.xpath(".//@data-gt-dealerzipcode")[0]
        street_address = raw_address.split(" - ")[0]
        if zip_code == "123456":
            zip_code = raw_address.split(", ")[2]
            street_address = ", ".join(raw_address.split(", ")[:2])
        city = raw_address.split(" - ")[1]
        latitude = ""
        longitude = ""

        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//div[@class="bottom-hours-item col-lg-4 "]/ul//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()]) if hoo else ""
        poi = loc_dom.xpath('//script[contains(text(), "PostalAddress")]/text()')
        if poi:
            poi = json.loads(poi[0])
            location_name = poi["name"]
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            zip_code = poi["address"]["postalCode"]
            phone = poi["telephone"].split(", ")[0]
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="RO",
            store_number="",
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
