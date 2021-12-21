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

    start_url = "https://loveforpilates.com/locations/"
    domain = "loveforpilates.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[span[@class="thumb-info-social-icons"]]')
    for poi_html in all_locations:
        page_url = poi_html.xpath(".//h3/a/@href")[0]
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h4/text()")[0]
        raw_address = poi_html.xpath(
            './/li[strong[contains(text(), "Address")]]/text()'
        )[-1]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = poi_html.xpath('.//li[strong[contains(text(), "Phone:")]]/text()')[
            -1
        ].strip()
        hoo = poi_html.xpath(
            './/h4[contains(text(), "Business ")]/following-sibling::ul[1]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        data = loc_dom.xpath('//div[contains(@id, "wpgmza_map")]/@data-settings')[0]
        data = json.loads(data)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number="",
            phone=phone,
            location_type="",
            latitude=data["map_start_lat"],
            longitude=data["map_start_lng"],
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
