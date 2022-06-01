# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://leeshoagiehouse.com/order/"
    domain = "leeshoagiehouse.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@target="_blank"]/@href')[:-1]
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h2/text()")[0]
        raw_address = " ".join(
            loc_dom.xpath('//p[@class="address-wrap"]/text()')
        ).replace("PA", "PA ")
        city = location_name.split(", ")[0]
        if "(Lehigh" not in raw_address:
            raw_address = raw_address.split("(")[0]
        phone = loc_dom.xpath(
            '//div[@class="col-12 col-lg-auto  text-center"]/p[3]/text()'
        )
        if not phone:
            phone = loc_dom.xpath(
                '//div[@class="col-12 col-lg-auto  text-center"]/p[5]/text()'
            )
        phone = phone[0] if phone else ""
        hoo = loc_dom.xpath(
            '//div[@class="col-12 col-lg-auto  text-center"]/p[4]/text()'
        )[1:]
        if phone == "Hours:":
            phone = loc_dom.xpath(
                '//div[@class="col-12 col-lg-auto  text-center"]/p[2]/text()'
            )[0]
            hoo = loc_dom.xpath(
                '//div[@class="col-12 col-lg-auto  text-center"]/p[3]/text()'
            )[1:]
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        if not hoo:
            hoo = loc_dom.xpath(
                '//p[contains(text(), "Hours:")]/following-sibling::p/text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])
        state = location_name.split(", ")
        if len(state) > 1:
            state = state[1]
        else:
            state = raw_address.split(",")[-1].split()[0]
        street_address = raw_address.split(city)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=raw_address.split()[-1],
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
