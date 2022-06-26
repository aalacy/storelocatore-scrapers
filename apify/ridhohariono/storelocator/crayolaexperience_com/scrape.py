# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.crayolaexperience.com/easton/contact-us"
    domain = "crayolaexperience.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="location"]//a[contains(text(), "Contact Us")]/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="section-heading"]/text()')[0]
        raw_data = loc_dom.xpath('//*[strong[contains(text(), "Address:")]]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if len(raw_data) == 5:
            raw_data = [raw_data[0]] + [", ".join(raw_data[2:4])] + raw_data[4:]
        if len(raw_data) > 3:
            raw_data = raw_data[1:]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        if not phone:
            phone = loc_dom.xpath('//p[a[contains(@href, "maps")]]/text()')[1].split(
                ":"
            )[1]
        geo = loc_dom.xpath('//a[contains(@href, "maps")]/@href')
        latitude = ""
        longitude = ""
        if geo:
            geo = geo[0].split("&ll=")[1].split("&")[0].split(",")
            latitude = geo[0]
            longitude = geo[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_data[1],
            city=raw_data[2].split(",")[0],
            state=raw_data[2].split(",")[1].split()[0],
            zip_postal=raw_data[2].split(",")[1].split()[1],
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
