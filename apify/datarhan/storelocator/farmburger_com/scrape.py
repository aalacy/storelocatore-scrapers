import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://farmburger.com/locations/"
    domain = "farmburger.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View Location")]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_address = loc_dom.xpath('//meta[@name="geo.placename"]/@content')
        raw_address = raw_address[0].split(", ") if raw_address else ""
        if not raw_address:
            raw_address = loc_dom.xpath(
                '//h5[contains(text(), "Find Us")]/following-sibling::p[1]/text()'
            )
            raw_address = raw_address[:1] + raw_address[1].split(", ")
        hoo = loc_dom.xpath(
            '//h5[contains(text(), "Hours")]/following-sibling::p/text()'
        )[0]
        if "NOW OPEN" in hoo:
            hoo = loc_dom.xpath(
                '//h5[contains(text(), "Hours")]/following-sibling::p/text()'
            )[1]
        phone = loc_dom.xpath(
            '//h5[contains(text(), "Take out")]/following-sibling::p[1]/text()'
        )
        if not phone:
            phone = loc_dom.xpath(
                '//h5[contains(text(), "Catering")]/following-sibling::p[1]/text()'
            )
        phone = phone[0] if phone else ""
        geo = loc_dom.xpath('//meta[@name="geo.position"]/@content')
        if geo:
            geo = geo[0].split(";")
            latitude = geo[0]
            longitude = geo[1]
        else:
            latitude = re.findall(r"lat: parseFloat\('(.+?)'\),", loc_response.text)[0]
            longitude = re.findall(r"lng: parseFloat\('(.+?)'\)", loc_response.text)[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[2].split()[0],
            zip_postal=raw_address[2].split()[-1],
            country_code="US",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
