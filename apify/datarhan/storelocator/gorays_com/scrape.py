import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "gorays.com"
    start_url = "https://www.gorays.com/StoreLocator/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath(
        '//*[contains(text(), "Our stores are in the following states:")]/following-sibling::div[1]//a/@href'
    )
    for url in all_states:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//td/a[contains(text(), "View")]/@href')

        for url in all_locations:
            store_url = urljoin(start_url, url)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            raw_address = loc_dom.xpath('//p[@class="Address"]/text()')
            raw_address = [elem.strip() for elem in raw_address if elem.strip()]
            location_name = loc_dom.xpath('//div[@class="container-fluid"]/h3/text()')
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = raw_address[0]
            location_type = "<MISSING>"
            city = raw_address[-1].split(", ")[0]
            state = raw_address[-1].split(", ")[-1].split()[0]
            zip_code = raw_address[-1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath('//p[@class="PhoneNumber"]/a/text()')
            phone = phone[0] if phone else "<MISSING>"
            geo = re.findall(r'initializeMap\("(.+?)"\);', loc_response.text)[0].split(
                '","'
            )
            latitude = geo[0]
            latitude = latitude if latitude else "<MISSING>"
            longitude = geo[1]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = loc_dom.xpath(
                '//dt[contains(text(), "Hours of Operation:")]/following-sibling::dd[1]/text()'
            )
            hours_of_operation = (
                hours_of_operation[0] if hours_of_operation else "<MISSING>"
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
