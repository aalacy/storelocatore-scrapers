# -*- coding: utf-8 -*-
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


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
            latitude = poi_html.xpath("@data-long")[0]
            longitude = poi_html.xpath("@data-lat")[0]
            location_name = " ".join(
                poi_html.xpath('.//span[@class="centre-heading"]/text()')
            )
            country_code = "https://www.kumonsearch.co.nz/".split(".")[-1].split("/")[0]
            url = poi_html.xpath('.//a[contains(text(), "More Info")]/@href')[0]
            page_url = urljoin(start_url, url)
            raw_address = poi_html.xpath(
                './/div[@class="centre-info no-number-label clearfix"]/p/text()'
            )
            phone = poi_html.xpath('.//a[contains(@href, "tel:")]/@href')
            phone = phone[0].split(":")[-1] if phone else ""
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            hoo = loc_dom.xpath(
                '//div[@class="study-periods-for-day-of-week clearfix"]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
            if ".au" in page_url:
                street_address = raw_address[1]
                city = " ".join(raw_address[-1].split()[:-2])
                state = raw_address[-1].split()[-2]
                zip_code = raw_address[-1].split()[-1]
            else:
                street_address = raw_address[0]
                city = " ".join(raw_address[-1].split()[:-2])
                state = raw_address[-1].split()[-2]
                zip_code = raw_address[-1].split()[-1]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
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
