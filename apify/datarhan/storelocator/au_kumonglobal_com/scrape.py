# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "kumonsearch.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    urls = ["https://www.kumonsearch.co.nz/", "https://www.kumonsearch.com.au/"]
    for start_url in urls:
        response = session.get(start_url, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//div[@class="centres"]/div')
        for poi_html in all_locations:
            longitude = poi_html.xpath("@data-long")[0]
            latitude = poi_html.xpath("@data-lat")[0]
            location_name = " ".join(
                poi_html.xpath('.//span[@class="centre-heading"]/text()')
            )
            url = poi_html.xpath('.//a[contains(text(), "More Info")]/@href')[0]
            page_url = urljoin(start_url, url)
            raw_address = poi_html.xpath(
                './/div[@class="centre-info no-number-label clearfix"]/p/text()'
            )
            raw_address = ", ".join([e.strip() for e in raw_address if e.strip()])
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2

            phone = poi_html.xpath('.//a[contains(@href, "tel:")]/@href')
            phone = phone[0].split(":")[-1] if phone else ""
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath(
                '//div[@class="study-periods-for-day-of-week clearfix"]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            country_code = start_url.split(".")[-1][:-1]
            if country_code == "au":
                city = " ".join(
                    raw_address.split(",")[-1].strip().split(" ")[:-2]
                ).strip()
            else:
                city = addr.city

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country_code,
                store_number="",
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hoo,
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
