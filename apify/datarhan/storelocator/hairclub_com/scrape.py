import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    domain = "hairclub.com"
    start_url = "https://www.hairclub.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Center Information")]/@href')
    for url in all_locations:
        store_url = "https://www.hairclub.com" + url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        address_raw = store_dom.xpath(
            '//ul[@class="center-info-address-list center-info-list list-unstyled"]/li/text()'
        )
        if len(address_raw) == 4:
            address_raw = (
                [address_raw[0]] + [", ".join(address_raw[1:3])] + address_raw[3:]
            )
        location_name = address_raw[0]
        street_address = address_raw[1].strip()
        city = address_raw[2].split(",")[0]
        state = address_raw[2].split(",")[-1].split()[0]
        zip_code = address_raw[2].split(",")[-1].split()[-1]
        store_number = re.findall(r"\d+", address_raw[0])
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = store_dom.xpath("//@data-js-web-phone")
        phone = phone[0].strip() if phone else ""
        phone = phone if phone else "<MISSING>"
        latitude = store_dom.xpath("//@data-js-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath("//@data-js-lon")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath(
            '//ul[@class="center-info-hours-list center-info-list list-unstyled"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=SgRecord.MISSING,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
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
