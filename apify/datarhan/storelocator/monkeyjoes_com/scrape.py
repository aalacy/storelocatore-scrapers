from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "moneymart.com"
    start_url = "https://www.monkeyjoes.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="locationBlock narrow"]/p[1]/a[@class="boldGreen"]/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="header-location"]/text()')[
            0
        ].strip()
        raw_address = loc_dom.xpath('//div[@class="loc-header-left"]/p/text()')
        raw_address = [
            elem.strip() for elem in raw_address if elem.strip() and "|" not in elem
        ]
        if len(raw_address) == 3:
            raw_address = [" ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0].strip()
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        phone = loc_dom.xpath('//div[@class="loc-header-left"]/p/a/text()')
        phone = phone[0] if phone else ""
        hoo = loc_dom.xpath('//h3[@id="hours"]/following-sibling::table[1]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
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
