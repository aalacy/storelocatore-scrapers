# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://www.holidayseniorliving.com/retirement-communities"
    domain = ""
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_states = dom.xpath(
        '//a[@class="super-footer-li-links" and contains(@href, "senior-living-communities")]/@href'
    )
    for url in all_states:
        state_url = urljoin(start_url, url)
        response = session.get(state_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="communityCard__info"]/div/a/@href')
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_address = loc_dom.xpath(
                '//p[@class="community-info__community-address"]/text()'
            )
            phone = loc_dom.xpath(
                '//div[@class="community-info__phone-number-container"]/a/text()'
            )
            phone = phone[0] if phone else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name="",
                street_address=raw_address[0].replace(",", ""),
                city=raw_address[1].split(",")[0],
                state=" ".join(raw_address[1].split(",")[1].split()[:-1]),
                zip_postal=raw_address[1].split(",")[1].split()[-1],
                country_code="",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation="",
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
