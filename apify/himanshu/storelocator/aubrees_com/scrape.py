# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://aubrees.com/locations"
    domain = "aubrees.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@data-uk-grid-match]//div[@class="uk-panel uk-panel-box"]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")[0].strip()
        raw_data = poi_html.xpath(".//h7/text()")[:2]
        raw_data = [e.strip() for e in raw_data if e.strip()]
        phone = poi_html.xpath(
            './/a[contains(text(), "Directions")]/following-sibling::b/text()'
        )[0].split("/")[0]
        hoo = poi_html.xpath(
            './/strong[contains(text(), "Hours of Operation:")]/following::text()'
        )
        hoo = " ".join(" ".join(hoo).split()).split("Buffet")[0].split("Happy")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_data[0].replace(",", ""),
            city=raw_data[1].split(", ")[0],
            state=raw_data[1].split(", ")[-1].split()[0],
            zip_postal=raw_data[1].split(", ")[-1].split()[-1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
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
