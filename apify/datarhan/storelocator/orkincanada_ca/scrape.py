from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "orkincanada.ca"
    start_url = "https://www.orkincanada.ca/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="card card--location"]/a[h3]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="card card--location"]/h3/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//div[@class="card card--location"]/div[@class="card--divider"][1]//text()'
        )
        raw_address = [
            elem.strip() for elem in raw_address if "Week" not in elem and elem.strip()
        ]
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//div[@class="card card--location"]/div[@class="card--divider"][2]//text()'
            )
        raw_address = [
            elem.strip() for elem in raw_address if "Week" not in elem and elem.strip()
        ]
        raw_address = " ".join(raw_address)
        adr = parse_address_intl(raw_address)
        street_address = adr.street_address_1
        if adr.street_address_2:
            street_address = adr.street_address_2 + " " + street_address
        city = adr.city
        state = adr.state
        zip_code = adr.postcode
        country_code = adr.country
        phone = loc_dom.xpath('//span[@class="card__phone"]/text()')
        phone = phone[0].split(": ")[-1] if phone else "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="card--divider"]/p/text()')
        hoo = [elem for elem in hoo if "Week" in elem]
        hours_of_operation = " ".join(hoo).replace("\n", "")

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
            location_type="",
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
