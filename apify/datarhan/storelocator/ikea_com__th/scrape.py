from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com/th/en/stores/"
    domain = "ikea.com/th"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//pub-hide-empty-link//a[contains(@href, "stores")]/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        geo = loc_dom.xpath('//a[contains(@href, "maps")]/@href')
        if geo and "/@" in geo[0]:
            geo = geo[0].split("/@")[-1].split(",")[:2]
        else:
            geo = loc_dom.xpath('//p[strong[contains(text(), "GPS code")]]/text()')[
                -1
            ].split(", ")
        hoo = loc_dom.xpath(
            '//p[strong[contains(text(), "WEEKDAY")]]/following-sibling::p[1]//text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[strong[contains(text(), "STORE OPENING HOURS")]]/following-sibling::p[1]//text()'
            )
        hoo = " ".join(hoo)
        raw_address = loc_dom.xpath('//p[strong[contains(text(), "Location")]]/text()')[
            1:
        ]
        raw_address = " ".join(raw_address)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = loc_dom.xpath('//a[contains(@title, "Call us")]/text()')
        phone = phone[0] if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="TH",
            store_number="",
            phone=phone,
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
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
