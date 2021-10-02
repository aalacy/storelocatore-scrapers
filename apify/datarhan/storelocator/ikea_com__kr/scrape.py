# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com/kr/en/stores/"
    domain = "ikea.com/kr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(@href, "/stores/") and span[@class="pub__btn__inner"]]/@href'
    )
    for page_url in all_locations:
        if "planning-studios" in page_url:
            continue

        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        location_name = loc_dom.xpath("//h1/text()")[0]
        raw_adr = loc_dom.xpath(
            '//h4[strong[contains(text(), "Address")]]/following-sibling::ul/li[1]/text()'
        )[0]
        addr = parse_address_intl(raw_adr)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = loc_dom.xpath('//li[strong[contains(text(), "Store")]]//text()')
        if not hoo:
            hoo = loc_dom.xpath('//li[contains(text(), "Store")]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = (
            " ".join(hoo)
            .replace("[", "")
            .replace("]", "")
            .replace("Store:", "")
            .replace("Store", "")
            .strip()
        )
        if hoo.startswith(":"):
            hoo = hoo[1:]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="KR",
            store_number="",
            phone="",
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
            raw_address=raw_adr,
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
