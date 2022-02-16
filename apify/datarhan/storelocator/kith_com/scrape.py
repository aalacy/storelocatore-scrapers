from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://kith.com/pages/locations"
    domain = "kith.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="page-location__location"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0].strip()
        raw_address = poi_html.xpath(
            './/p[@class="page-location__location-address"]/text()'
        )
        raw_address = [e.strip() for e in raw_address]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        if location_name == "Brooklyn":
            city = "New York"
        if city.lower() == "ny":
            city = "New York"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        raw_hoo = poi_html.xpath('.//p[@class="page-location__location-hours"]//text()')
        raw_hoo = [e.strip() for e in raw_hoo if e.strip()]
        phone = [e for e in raw_hoo if "+" in e or e.startswith("(")]
        phone = phone[0] if phone else ""
        geo = poi_html.xpath(".//h2/a/@href")[0]
        latitude = ""
        longitude = ""
        if geo:
            geo = geo.split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]
        hoo = [e for e in raw_hoo if "(" not in e]
        hours_of_operation = (
            " ".join(hoo).split("Christmas Eve")[0].split("+")[0].strip()
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
