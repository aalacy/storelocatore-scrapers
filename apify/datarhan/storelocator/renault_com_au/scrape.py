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

    start_url = "https://www.renault.com.au/find-a-dealer/"
    domain = "renault.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="findDealerCtaWrappers"]/a[contains(@href, "dealer-info.asp")]/@href'
    )
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="locateDealerInfoHeading"]/text()')[
            0
        ]
        street_address = loc_dom.xpath(
            '//div[contains(text(), "Address:")]/following-sibling::div[1]/text()'
        )[0]
        raw_data = loc_dom.xpath(
            '//div[contains(text(), "Address:")]/following-sibling::div[2]/text()'
        )[0].split(",")
        phone = loc_dom.xpath(
            '//div[contains(text(), "Phone:")]/following-sibling::div[1]/text()'
        )[0].split(",")[0]
        types = loc_dom.xpath(
            '//div[h2[@class="locateDealerInfoHeading"]]/following-sibling::div[1]//svg/@class'
        )
        location_type = ", ".join([e.split("-svg-")[-1] for e in types])
        hoo = loc_dom.xpath(
            '//div[@data-id="ldidSales"]//div[contains(text(), "Trading Hours:")]/following-sibling::div[1]//text()'
        )
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=raw_data[0],
            state=raw_data[1],
            zip_postal=raw_data[2],
            country_code=raw_data[3],
            store_number=page_url.split("=")[-1],
            phone=phone,
            location_type=location_type,
            latitude="",
            longitude="",
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
