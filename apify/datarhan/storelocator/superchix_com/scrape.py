from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.superchix.com/#LOCATIONS"
    domain = "superchix.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[b[contains(text(), "ADDRESS:")]]')
    all_locations += dom.xpath('//div[p[span[contains(text(), "ADDRESS:")]]]')
    for poi_html in all_locations:
        raw_address = poi_html.xpath(".//text()")[1:]
        raw_address = [e.strip() for e in raw_address]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        location_name = f"{city}, {state}"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        phone = poi_html.xpath(
            './/following-sibling::div[b[contains(text(), "CONTACT:")]]/div/text()'
        )
        if not phone:
            phone = poi_html.xpath(
                './/div[b[contains(text(), "CONTACT:")]]/following-sibling::div//text()'
            )
        phone = phone[0].strip() if phone else ""
        if not phone:
            phone = poi_html.xpath(
                './/following-sibling::div/p[span[contains(text(), "CONTACT:")]]/following-sibling::p[1]/span/text()'
            )
        if not phone:
            phone = poi_html.xpath(
                './/p[span[contains(text(), "CONTACT:")]]/following-sibling::p[1]/span/text()'
            )
        if not phone:
            phone = poi_html.xpath(
                './/div[b[contains(text(), "CONTACT:")]]/following-sibling::span/div/b/span/text()'
            )
        if type(phone) == list:
            phone = phone[0] if phone else "<MISSING>"
        else:
            phone = phone if phone else "<MISSING>"
        if phone == "<MISSING>":
            continue
        hoo = poi_html.xpath(
            './/following-sibling::div[descendant::*[contains(text(), "HOURS:")]]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).split("HOURS:")[-1] if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type="",
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
