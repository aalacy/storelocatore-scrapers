from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()
MISSING = SgRecord.MISSING

start_url = "https://www.jrff.co.jp/cinnabon/location/"


def get_address(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception:
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():

    domain = "jrff.co.jp"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[contains(@class, "edgtf-elements-holder edgtf-three-columns")]/div'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h5/strong/span/text()")
        if not location_name:
            continue
        location_name = location_name[0]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        raw_adr = poi_html.xpath(".//p[strong]/text()")
        raw_adr = " ".join([e.strip() for e in raw_adr if e.strip()])
        street_address, city, state, zip_postal = get_address(raw_adr)
        raw_address = raw_adr

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code="JP",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
