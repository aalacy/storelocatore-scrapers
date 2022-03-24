from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.co.il/retailers/#introduction"
    domain = "lexus.co.il"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="c-body-content-text" and h3]')
    for poi_html in all_locations:
        location_name = " ".join(poi_html.xpath(".//h3/span/text()"))
        if "אולם תצוגה" not in location_name:
            continue
        raw_address = poi_html.xpath(
            './/div[@class="c-body-content-text__body ui-rich-text"]/p/text()'
        )[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        raw_data = poi_html.xpath(
            './/div[@class="c-body-content-text__body ui-rich-text"]/p/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        phone = [e.split(":")[-1].strip() for e in raw_data if "טלפון" in e][0]
        hoo = [e for e in raw_data if "0 - " in e]
        hoo = " ".join([e for e in hoo]).split("04-")[0].strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state="",
            zip_postal=addr.postcode,
            country_code="IL",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
