import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    start_url = "https://www.converse.com/stores-all"
    domain = "converse.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@class, "store-link")]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[contains(@class, "store-name")]/text()')[
            0
        ].strip()
        raw_address = loc_dom.xpath("//address/text()")
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        phone = loc_dom.xpath(
            '//a[@class="store-locator-details__mobile-button--phone"]/text()'
        )
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = loc_dom.xpath(
            '//span[@class="store-locator-details__store-type__text text--capitalize"]/text()'
        )
        location_type = location_type[0].strip() if location_type else ""
        geo = json.loads(loc_dom.xpath("//div/@data-single-marker-map")[0])
        latitude = geo["lat"]
        longitude = geo["lng"]
        hoo = loc_dom.xpath(
            '//span[contains(text(), "Hours")]/following-sibling::div/text()'
        )
        hoo = [e.strip().replace("\n", "") for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo)
            .split("New")[0]
            .split("Temporary")[0]
            .split("Holiday")[0]
            .strip()
            if hoo
            else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
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
