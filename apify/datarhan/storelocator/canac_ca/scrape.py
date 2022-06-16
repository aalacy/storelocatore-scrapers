from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://www.canac.ca/en/#"
    domain = "canac.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="store-locator-popup-selector"]')
    for poi_html in all_locations:
        raw_address = poi_html.xpath(
            './/div[@class="store-locator-address-container-text"]/text()'
        )
        raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
        addr = parse_address_intl(raw_address)
        zip_code = addr.postcode.replace("LÉVIS", "")
        location_name = raw_address.split(zip_code)[-1].strip()
        raw_address = raw_address.replace(location_name, "")
        addr = parse_address_intl(raw_address)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=poi_html.xpath(
                './/div[@class="store-locator-address-container-text"]/text()'
            )[0],
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code="CA",
            store_number=poi_html.xpath("@data-store-id")[0],
            phone="",
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
