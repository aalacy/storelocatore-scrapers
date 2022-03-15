from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "tommybahama.com"
    start_url = "https://www.tommybahama.com/restaurants/restaurants.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@class="imagetext-location"]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h3[@class="cmp-title__text"]/text()')
        location_name = (
            location_name[-1].strip() if location_name[-1].strip() else "<MISSING>"
        )
        street_address = loc_dom.xpath(
            '//p[*[*[a[contains(@href, "/maps/")]]]]/preceding-sibling::p[3]/text()'
        )
        if not street_address:
            street_address = loc_dom.xpath(
                '//p[contains(text(), "Restaurant & Bar")]/following-sibling::p/text()'
            )
            street_address = [[e.strip() for e in street_address if e.strip()][-2]]
        street_address = street_address[0]
        raw_data = loc_dom.xpath(
            '//p[*[*[a[contains(@href, "/maps/")]]]]/preceding-sibling::p[2]/text()'
        )
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//p[contains(text(), "Restaurant & Bar")]/following-sibling::p/text()'
            )
            raw_data = [[e.strip() for e in raw_data if e.strip()][-1]]
        raw_data = raw_data[0]
        city = raw_data.split(", ")[0]
        state = raw_data.split(", ")[-1].split()[0]
        zip_code = raw_data.split(", ")[-1].split()[-1]
        phone = loc_dom.xpath('//p[contains(text(), "Phone")]/text()')
        if phone:
            phone = phone[0].replace("Phone: ", "")
        if not phone:
            phone = loc_dom.xpath(
                '//p[b[contains(text(), "Store")]]/following-sibling::p[1]/b/text()'
            )
            phone = phone[0] if phone else ""
        if not phone:
            phone = loc_dom.xpath(
                '//p[contains(text(), "Restaurant & Bar")]/following-sibling::p[1]/text()'
            )
            phone = phone[0] if phone and phone[0] != "Open:" else ""
        hours_of_operation = (
            loc_dom.xpath('//p[contains(text(), "Open:")]/text()')[-1]
            .replace("Open:", "")
            .replace("|", ",")
        )
        if not hours_of_operation:
            hours_of_operation = (
                loc_dom.xpath('//p[contains(text(), "Open:")]/text()')[0]
                .replace("Open:", "")
                .replace("|", ",")
            )
        if not hours_of_operation:
            hours_of_operation = loc_dom.xpath(
                '//p[contains(text(), "Open:")]/following-sibling::p[1]/text()'
            )[0]
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"
        hours_of_operation = hours_of_operation.split("Happy")[0].strip()
        if hours_of_operation == "Mon-Fri: 11:30AM-8PM":
            hours_of_operation = " ".join(
                loc_dom.xpath(
                    '//p[contains(text(), "Open:")]/following-sibling::p[1]/text()'
                )[:3]
            )
        hours_of_operation = hours_of_operation.replace("|", "")
        location_type = ""
        if (
            "The restaurant is temporarily closed"
            in loc_dom.xpath('//h3[@class="cmp-title__text"]/text()')[0]
        ):
            location_type = "temporarily closed"
        if "COCONUT" in location_name:
            phone = "239.947.2203"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
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
