# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://www.steward.org/network/our-hospitals",
        "https://www.steward.org/network/hospitals/international",
    ]
    domain = "steward.org"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//div[@class="state-location"]')
        for poi_html in all_locations:
            location_name = " ".join(poi_html.xpath(".//h3/text()")[0].split())
            raw_address = poi_html.xpath(
                './/h4[contains(text(), "Hospital Address")]/following-sibling::div/text()'
            )
            raw_address = [e.strip() for e in raw_address if e.strip()]
            phone = poi_html.xpath('.//a[@class="phone"]/@href')[0].split(":")[-1]
            country_code = "United States"
            street_address = raw_address[0]
            city = raw_address[1].split(", ")[0]
            state = raw_address[1].split(", ")[-1].split()[0]
            zip_code = raw_address[1].split(", ")[-1].split()[-1]
            raw_address = " ".join(raw_address)
            if "international" in start_url:
                addr = parse_address_intl(raw_address)
                country_code = addr.country
                city = addr.city
                zip_code = addr.postcode
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address += ", " + addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
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
                hours_of_operation="",
                raw_address=raw_address,
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
