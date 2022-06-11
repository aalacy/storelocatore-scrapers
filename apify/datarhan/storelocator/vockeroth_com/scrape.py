# -*- coding: utf-8 -*-
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.vockeroth.com/modehaeuser/"
    domain = "vockeroth.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//p/a[@class="btn btn-primary btn-block"]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="vc_custom_heading"]/text()')[0]
        raw_address = loc_dom.xpath('//p[strong[contains(text(), "Anschrift")]]/text()')
        raw_address = [e.strip() for e in raw_address]
        phone = loc_dom.xpath('//p[strong[contains(text(), "Kontakt")]]/text()')[
            0
        ].split(":")[-1]
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        hoo = loc_dom.xpath('//p[strong[contains(text(), "Öffnungszeiten")]]/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        street_address = ", ".join(raw_address[:2])
        city = raw_address[-1].split()[-1]
        zip_code = raw_address[-1].split()[0]
        street_address = street_address.split(zip_code)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="",
            store_number="",
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
