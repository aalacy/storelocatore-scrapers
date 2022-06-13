import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "myrighttime.com"
    start_url = "https://www.myrighttime.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//h3[b[contains(text(), "IN-PERSON VISITS")]]/following-sibling::p[2]//a/@href'
    )

    for store_url in all_locations:
        if "http" not in store_url:
            store_url = urljoin("https://www.myrighttime.com/", store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        poi = loc_dom.xpath('//script[contains(text(), "postalCode")]/text()')
        if poi:
            poi = demjson.decode(poi[0])
            street_address = poi["address"]["streetAddress"]
            city = poi["address"]["addressLocality"]
            state = poi["address"]["addressRegion"]
            zip_code = poi["address"]["postalCode"]
            phone = poi["telephone"]
        else:
            raw_adr = loc_dom.xpath('//a[contains(@href, "g.page")]/text()')
            if not raw_adr:
                raw_adr = loc_dom.xpath('//a[contains(@href, "goo.gl")]/text()')
            street_address = raw_adr[0]
            city = raw_adr[1].split(", ")[0].strip()
            state = raw_adr[1].split(", ")[-1].split()[0]
            zip_code = raw_adr[1].split(", ")[-1].split()[-1]
            phone = loc_dom.xpath(
                '//p[font[contains(text(), "To speak to a representative, please call ")]]/text()'
            )
            phone = phone[-1] if phone else ""
        hoo = loc_dom.xpath(
            '//span[contains(text(), "Hours of operation")]/following-sibling::p/text()'
        )
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else ""
        longitude = loc_dom.xpath("//@data-lon")
        longitude = longitude[0] if longitude else ""
        if street_address.endswith(","):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
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
