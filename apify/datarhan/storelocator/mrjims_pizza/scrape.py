import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "mrjims.pizza"
    start_url = "https://mrjims.pizza/storepages.cfm"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_store_numbers = dom.xpath('//select[@name="store_franchise_id"]/option/@value')
    for store_number in all_store_numbers:
        if not store_number:
            continue
        page_url = f"https://mrjims.pizza/{store_number}.cfm"
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        days = loc_dom.xpath(
            '//div[contains(text(), "Hours")]/following-sibling::div[1]/div[1]/div/text()'
        )
        hours = loc_dom.xpath(
            '//div[contains(text(), "Hours")]/following-sibling::div[1]/div[2]/div/text()'
        )
        hours = [e.strip() for e in hours if e.strip()]
        hoo = list(map(lambda d, h: d + " " + h, days, hours))
        hoo = " ".join(hoo) if hoo else ""
        location_name = loc_dom.xpath('//div[@class="RedHeadBig"]/text()')[0].strip()
        phone = re.findall("Store Phone: (.+) <", loc_response.text)
        phone = phone[0] if phone else ""
        street_address = loc_dom.xpath(
            '//div[contains(text(), "Address")]/following-sibling::div[1]/text()'
        )[0].strip()
        street_address_2 = loc_dom.xpath(
            '//div[contains(text(), "Address")]/following-sibling::div[2]/text()'
        )[0].strip()
        if street_address_2 and "Suite" in street_address_2:
            street_address += ", " + street_address_2
        city = (
            loc_dom.xpath(
                '//div[contains(text(), "Address")]/following-sibling::div[3]/text()'
            )[0]
            .strip()
            .split(",")[0]
        )
        state = (
            loc_dom.xpath(
                '//div[contains(text(), "Address")]/following-sibling::div[3]/text()'
            )[0]
            .strip()
            .split(",")[-1]
            .split()[0]
        )
        zip_code = (
            loc_dom.xpath(
                '//div[contains(text(), "Address")]/following-sibling::div[3]/text()'
            )[0]
            .strip()
            .split(",")[-1]
            .split()[-1]
        )
        geo = (
            loc_dom.xpath('//a[contains(text(), " View in Google Maps ")]/@href')[0]
            .split("=")[-1]
            .split(",")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
