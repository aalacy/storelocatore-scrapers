from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests(verify_ssl=False)
    domain = "getairsports.com"
    start_url = "https://getairsports.com/park-locator/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="states defaults"]//a/@href')
    all_locations += dom.xpath('//div[@class="statess"]//a/@href')

    for store_url in all_locations:
        store_url = store_url.replace("http:", "https:")
        loc_response = session.get(store_url, headers=hdr)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)
        if "getairsports.com" not in store_url:
            continue
        if loc_dom.xpath('//h5[contains(text(), "PERMANENTLY CLOSED")]'):
            continue
        location_name = loc_dom.xpath('//meta[@property="og:site_name"]/@content')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//a[@class="local-address"]/text()')
        if not address_raw:
            continue
        if loc_dom.xpath('//h5[contains(text(), "ly Closed")]'):
            continue
        address_raw = address_raw[0]
        addr = parse_address_intl(address_raw)
        phone = loc_dom.xpath('//a[@class="local-number"]/text()')
        phone = phone[0] if phone else ""
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        country_code = "USA" if len(addr.postcode.split()) == 1 else "CA"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
