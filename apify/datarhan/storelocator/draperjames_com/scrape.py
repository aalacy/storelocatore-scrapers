from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://draperjames.com/pages/store-locator"
    domain = "draperjames.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="store-location"]')
    for poi_html in all_locations:
        store_url = start_url
        location_name = "".join(
            poi_html.xpath('.//h4[@class="store-location__location"]/text()')
        )
        if "Permanently Closed" in location_name:
            continue

        raw_data = poi_html.xpath('.//div[@class="store-location__address"]//text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = poi_html.xpath('.//div[@class="store-location__address"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip() and "(" not in e]
        raw_address = " ".join(raw_data[:-1]).replace("\n", ", ")
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address.split("Location Address ")[-1]
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        phone = [e for e in raw_data if "(" in e][0]
        location_type = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="store-location__hours-details"]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude="",
            longitude="",
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
