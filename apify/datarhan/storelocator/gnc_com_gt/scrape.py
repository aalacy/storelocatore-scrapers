from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://gnc.com.gt/pages/nuestras-tiendas-1"
    domain = "gnc.com.gt"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//article[@class="item-content"]/div/div[p[strong]]')
    all_locations += dom.xpath(
        '//article[@class="item-content"]/div[@data-icon="gpicon-accordion"]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//strong/text()")
        location_name = " ".join([e.strip() for e in location_name if e.strip()])
        raw_address = poi_html.xpath(".//p/span/text()")
        raw_address += poi_html.xpath(".//p/text()")
        raw_address = [e.strip() for e in raw_address if e.strip() and "Tel." not in e]
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath('.//*[contains(text(), "Tel.")]/text()')
        phone = phone[0].replace("Tel.", "").split("/")[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
            raw_address=raw_address,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.RAW_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
