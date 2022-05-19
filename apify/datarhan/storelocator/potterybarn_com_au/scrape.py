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

    start_url = "https://www.potterybarn.com.au/store-locations"
    domain = "potterybarn.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Store Hours & Details")]/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//div[@class="bondi-junction-header"]/h3/text()'
        )[0]
        if "Outlet" in location_name:
            location_name = "Pottery Barn Outlet"
        else:
            location_name = "Pottery Barn"
        raw_data = loc_dom.xpath(
            '//td[@class="bondi-junction-table-big-padding-cell"]/text()'
        )
        raw_data = [
            e.replace("\xa0", "") for e in raw_data if e.strip() and "Phone" not in e
        ]
        raw_address = " ".join(" ".join(raw_data).split())
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if street_address == "100":
            street_address = "100 Bulla Road"
        phone = loc_dom.xpath('//a[contains(@onclick, "tel")]/text()')[0]
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        hoo = loc_dom.xpath(
            '//tr[td[b[contains(text(), "Regular Trading Hours:")]]]/following-sibling::tr/td/text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        city = addr.city
        if not city:
            city = page_url.split("/")[-1].capitalize()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="AU",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[1],
            longitude=geo[0],
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
