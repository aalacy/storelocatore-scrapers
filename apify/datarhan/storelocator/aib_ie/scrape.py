from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://aib.ie/content/dam/aib/personal/docs/our-products/mortgages/get-branches.xml/jcr:content/renditions/original"
    domain = "aib.ie"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.XML(response.text.encode("ascii"))

    all_locations = dom.xpath("//location")
    for poi_html in all_locations:
        poi_data = etree.HTML(poi_html.xpath("//tab/text()")[0])
        location_name = poi_html.xpath(".//name/text()")
        if not location_name:
            location_name = poi_data.xpath(
                '//td[contains(text(), "Branch")]/following-sibling::td[1]/text()'
            )
        location_name = location_name[0] if location_name else ""
        store_number = poi_data.xpath(
            '//td[contains(text(), "Sort Code")]/following-sibling::td[1]/text()'
        )[0]
        store_number = store_number[0] if store_number else ""
        raw_address = poi_html.xpath(".//branchAddress/text()")
        if not raw_address:
            raw_address = poi_data.xpath(
                '//td[contains(text(), "Address")]/following-sibling::td[1]/text()'
            )
        raw_address = raw_address[0].replace("\n", " ")
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        state = poi_html.xpath(".//brancharea/text()")
        state = state[0] if state else ""
        if not state:
            state = addr.state
        latitude = poi_html.xpath(".//lat/text()")
        latitude = latitude[0] if latitude else ""
        longitude = poi_html.xpath(".//long/text()")
        longitude = longitude[0] if longitude else ""
        phone = etree.HTML(poi_html.xpath(".//tab/text()")[0]).xpath(
            './/td[contains(text(), "Telephone")]/following-sibling::td[1]/text()'
        )
        if not phone:
            phone = poi_data.xpath(
                '//td[contains(text(), "Telephone")]/following-sibling::td[1]/text()'
            )
        phone = phone[0] if phone else ""
        page_url = etree.HTML(poi_html.xpath(".//tab/text()")[0]).xpath(".//a/@href")
        page_url = page_url[0] if page_url else ""
        hoo = etree.HTML(poi_html.xpath(".//tab/text()")[1]).xpath(".//text()")
        hoo = [e.strip() for e in hoo if e.strip() and "This" not in e]
        hoo = " ".join(hoo)
        location_type = ""
        if "Closed due to Covid" in hoo:
            hoo = ""
            location_type = "Closed due to Covid"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=state,
            zip_postal=addr.postcode,
            country_code="IE",
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
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
