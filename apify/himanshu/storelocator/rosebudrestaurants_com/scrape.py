from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://rosebudrestaurants.com/"
    domain = "rosebudrestaurants.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(text(), "Locations")]/following-sibling::ul//a/@href'
    )
    for page_url in list(set(all_locations)):
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h1[@class="elementor-heading-title elementor-size-default"]/text()'
        )
        location_name = location_name[0] if location_name else ""
        raw_data = loc_dom.xpath(
            '//div[@class="elementor-container elementor-column-gap-default"]//p[@class="elementor-heading-title elementor-size-default"]/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]

        addr = parse_address_intl(raw_data[0])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else ""
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        phone = raw_data[1]
        hoo = loc_dom.xpath(
            '//div[div[h6[contains(text(), "Regular Hours")]]]/following-sibling::div[1]//li/text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()]).split("Lunch")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
