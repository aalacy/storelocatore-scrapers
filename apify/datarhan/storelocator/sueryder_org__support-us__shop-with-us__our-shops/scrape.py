# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sueryder.org/support-us/shop-with-us/our-shops?postcode={}"
    domain = "sueryder.org/support-us/shop-with-us/our-shops"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], expected_search_radius_miles=10
    )
    for code in all_codes:
        response = session.get(start_url.format(code.replace(" ", "+")), headers=hdr)
        if response.status_code != 200:
            continue
        dom = etree.HTML(response.text)

        all_locations = dom.xpath(
            '//div[@class="listing--block listing--block--shops"]//a/@href'
        )
        for url in all_locations:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath("//h1/span/text()")[0]
            street_address = loc_dom.xpath('//span[@class="address-line1"]/text()')[0]
            st_adr_2 = loc_dom.xpath('//span[@class="address-line2"]/text()')
            if st_adr_2:
                street_address += ", " + st_adr_2[0]
            city = loc_dom.xpath('//span[@class="locality"]/text()')[0]
            zip_code = loc_dom.xpath('//span[@class="postal-code"]/text()')[0]
            country_code = loc_dom.xpath('//span[@class="country"]/text()')[0]
            phone = loc_dom.xpath('//span[contains(text(), "T:")]/following::text()')
            phone = phone[0].strip() if phone else ""
            latitude = loc_dom.xpath("//@data-lat")[0]
            longitude = loc_dom.xpath("//@data-lng")[0]
            hoo = loc_dom.xpath(
                '//div[contains(text(), "Opening hours")]/following-sibling::div[1]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state="",
                zip_postal=zip_code,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
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
