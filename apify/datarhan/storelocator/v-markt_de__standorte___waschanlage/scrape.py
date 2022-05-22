# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.v-markt.de/standorte_waschanlage"
    domain = "v-markt.de/standorte_waschanlage"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//select[@id="favoriten"]/option')[1:]
    for l in all_locations:
        store_number = l.xpath("@value")[0]
        location_name = l.xpath("text()")[0]
        page_url = f"https://www.v-markt.de/so/{location_name.replace(' ', '-')}/{store_number}"
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_data = loc_dom.xpath('//div[div[@class="section-title"]]/div[3]/p//text()')
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//div[@class="row"]/div[@class="col-md-6"]/p//text()'
            )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        geo = (
            loc_dom.xpath('//a[i[@class="icon-left fa fa-car"]]/@href')[0]
            .split("=")[-1]
            .split(",")
        )
        hoo = loc_dom.xpath(
            '//section[@id="waschstrasse"]//tr[td[contains(text(), "Montag")]]//text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_data[0],
            city=" ".join(raw_data[1].split()[1:]),
            state="",
            zip_postal=raw_data[1].split()[0],
            country_code="DE",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
