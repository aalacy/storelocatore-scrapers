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

    start_url = "https://www.cora.be/fr/choix-du-magasin"
    domain = "cora.be"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="ca-PrehomeShop-pinsContainer "]/div')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0].strip()
        street_address = poi_html.xpath(
            './/div[@class="ca-PinsPanel-subTitle"]/text()'
        )[0].strip()
        page_url = poi_html.xpath(".//a/@href")[0]
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath("//address/text()")[-1].split(":")[-1]
        hoo = loc_dom.xpath('//ul[@class="ca-MiscStore-openingList"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        country_code = "BE"
        if ".lu" in page_url:
            country_code = "LU"

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=location_name,
            state="",
            zip_postal="",
            country_code=country_code,
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
