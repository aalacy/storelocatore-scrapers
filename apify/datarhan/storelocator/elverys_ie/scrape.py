# -*- coding: utf-8 -*-
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgselenium.sgselenium import SgFirefox


def fetch_data():
    session = SgRequests()
    start_url = (
        "https://www.elverys.ie/store-finder?latitude=0.0&longitude=0.0&q=&page=0"
    )
    domain = "elverys.ie"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//form[contains(@id, "bindStore")]/@action')
    total_pages = dom.xpath('//div[@class="cus-pagnation"]/div/text()')[0][-1]
    for p in range(1, int(total_pages)):
        np = f"https://www.elverys.ie/store-finder?latitude=0.0&longitude=0.0&q=&page={p}"
        response = session.get(np)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//form[contains(@id, "bindStore")]/@action')

    for url in all_locations:
        page_url = "https://www.elverys.ie" + url
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(
            loc_response.text.replace('17 O" Connell', "17 O Connell")
            .replace('Baker" s Lane', "Baker s Lane")
            .replace('7 O" Connell', "7 O Connell")
        )

        location_name = loc_dom.xpath('//div[@class="col-sm-8 store"]//h5/text()')[1]
        poi = loc_dom.xpath("//@data-stores")[0]
        if not poi.endswith('"}'):
            poi = poi + '"}'
        poi = demjson.decode(poi)
        poi_html = etree.HTML(poi["name"])
        raw_address = (
            ", ".join(poi_html.xpath("//div/text()")[1:])
            .replace("< div>", "")
            .split(", ")
        )
        phone = (
            loc_dom.xpath(
                '//h5[contains(text(), "Telephone")]/following-sibling::p[1]/text()'
            )[0]
            .split("s")[-1]
            .split("E")[0]
            .strip()
        )
        hoo = loc_dom.xpath('//table[@class="store-openings weekday_openings"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        street_address = ", ".join(raw_address[:-3])
        city = raw_address[-3].replace("16", "")
        zip_code = raw_address[-2]
        if city == "Edward Square":
            street_address += ", " + city
            city = zip_code
            zip_code = ""
        if "682" in phone:
            with SgFirefox() as driver:
                driver.get(page_url)
                loc_dom = etree.HTML(driver.page_source)
            phone = (
                loc_dom.xpath(
                    '//h5[contains(text(), "Telephone")]/following-sibling::p[1]/text()'
                )[0]
                .split("E")[0]
                .strip()
            )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=raw_address[-1],
            store_number="",
            phone=phone,
            location_type="",
            latitude=poi["latitude"],
            longitude=poi["longitude"],
            hours_of_operation=hoo,
            raw_address=", ".join(raw_address),
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
