import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "buildwithbmc.com"
    start_url = "https://www.buildwithbmc.com/bmc/store-finder"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//input[@class="region-iso"]/@value')
    for state in all_states:
        state_url = "https://www.buildwithbmc.com/bmc/store-finder?region=US-{}".format(
            state
        )
        response = session.get(state_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//div[@class="section2 search-result-item"]//a[contains(text(), "More Details")]/@href'
        )

        for url in list(set(all_locations)):
            store_url = urljoin(start_url, url)
            store_response = session.get(store_url)
            if store_response.status_code != 200:
                continue
            dom = etree.HTML(store_response.text)
            store_data = dom.xpath('//div[@id="map_canvas"]/@data-stores')
            if not store_data:
                continue
            store_data = json.loads(store_data[0])

            address_raw = etree.HTML(store_data["name"])
            address_raw = address_raw.xpath("//text()")
            if len(address_raw) == 6:
                address_raw = [
                    address_raw[0],
                    ", ".join(address_raw[1:3]),
                ] + address_raw[3:]
            location_name = address_raw[0]
            street_address = address_raw[1]
            city = address_raw[2]
            address_raw_2 = dom.xpath('//div[@class="detailSection section2"]/text()')
            address_raw_2 = [elem.strip() for elem in address_raw_2 if elem.strip()]
            state = address_raw_2[1].split(",")[-1].split()[0]
            zip_code = address_raw[3]
            country_code = address_raw[-1]
            store_number = dom.xpath('//input[@id="storename"]/@value')[0]
            phone = dom.xpath(
                '//a[@class="phone-number phone-format bold-font"]/text()'
            )
            phone = phone[0] if phone else "<MISSING>"
            location_type = dom.xpath(
                '//h3[contains(text(), "Facility Type")]/following-sibling::div//label/text()'
            )
            location_type = ", ".join(location_type) if location_type else "<MISSING>"
            latitude = store_data["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = store_data["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = dom.xpath(
                '//div[@class="section1 puckup-hours section2"]/div//text()'
            )
            hours_of_operation = [
                elem.strip()
                for elem in hours_of_operation
                if elem.strip() and "/" not in elem
            ]
            hours_of_operation = [
                " ".join([e.strip() for e in elem.split()])
                for elem in hours_of_operation
            ]
            hours_of_operation = " ".join(hours_of_operation)
            hours_of_operation = (
                hours_of_operation.replace(": - Monday", "Monday")
                if hours_of_operation
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
                store_number=store_number,
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
