# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
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

    start_url = "https://www.suzuki.co.nz/cars/find-a-dealer"
    domain = "suzuki.co.nz"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[@data-lat]")
    for poi_html in all_locations:
        page_url = poi_html.xpath("@data-url")[0]
        page_url = urljoin(start_url, page_url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@id="dealerName"]/text()')[0]
        latitude = poi_html.xpath("@data-lat")[0]
        longitude = poi_html.xpath("@data-lng")[0]
        state = poi_html.xpath(".//h6/text()")[0]
        phone = poi_html.xpath(".//ul/li/text()")[0].strip().split("or")[0].strip()
        raw_address = loc_dom.xpath('//h3[@class="address"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(", ".join(raw_address))
        location_type = loc_dom.xpath('//ul[@class="services"]/li/text()')
        location_type = " ".join(location_type)
        if "Sales" not in location_type:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=addr.city,
            state=state,
            zip_postal=addr.postcode,
            country_code="NZ",
            store_number="",
            phone=phone,
            location_type=location_type,
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
