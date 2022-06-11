from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.brainbalancecenters.com/locations?zip="
    domain = "brainbalancecenters.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[@data-x5-centers-item]")
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[contains(text(), "Go to website")]/@href')[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi_html.xpath(".//h3/text()")[0].strip()
        raw_adr = poi_html.xpath(
            './/h4[contains(text(), "Location")]/following-sibling::p[1]/text()'
        )
        raw_adr = ", ".join([e.strip() for e in raw_adr if e.strip()])
        addr = parse_address_intl(raw_adr)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = poi_html.xpath('.//p[@class="phone"]/text()')[0]
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lng")[0]
        hoo = loc_dom.xpath('//div[h4[contains(text(), "Hours")]]/p/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
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
