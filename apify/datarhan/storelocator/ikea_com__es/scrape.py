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

    start_url = "https://www.ikea.com/es/en/stores/"
    domain = "ikea.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@href, "/stores/")]/@href')
    for page_url in all_locations:
        if page_url == "https://www.ikea.com/es/en/stores/":
            continue
        loc_response = session.get(page_url)
        if loc_response.status_code != 200:
            continue
        if "ikea-dis" in page_url:
            continue
        loc_dom = etree.HTML(loc_response.text)
        raw_adr = loc_dom.xpath('//p[strong[contains(text(), "Address")]]/a/text()')
        if not raw_adr:
            raw_adr = loc_dom.xpath(
                '//p[strong[contains(text(), "How to get here")]]/following-sibling::p/a/text()'
            )
        if not raw_adr:
            raw_adr = loc_dom.xpath(
                '//p[strong[contains(text(), "Address")]]/following-sibling::p/a/text()'
            )
        if not raw_adr:
            raw_adr = loc_dom.xpath(
                '//p[strong[contains(text(), "Adress")]]/strong/a/text()'
            )
        if not raw_adr:
            continue
        addr = parse_address_intl(" ".join(raw_adr))
        location_name = loc_dom.xpath('//h2[contains(text(), "Offers IKEA")]/text()')
        if not location_name:
            location_name = loc_dom.xpath("//h1/text()")
        location_name = location_name[0].replace("Offers", "").strip()
        if "Planning Studio" in location_name:
            continue
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[-1] if phone else ""
        hoo = loc_dom.xpath(
            '//div[p[strong[contains(text(), "Store opening hours")]]]/p//text()'
        )
        if not hoo:
            hoo = loc_dom.xpath('//p[strong[contains(text(), "Schedule:")]]/text()')
        if not hoo:
            hoo = loc_dom.xpath(
                '//li[strong[contains(text(), "Schedule:")]]/strong/text()'
            )[1:]
        if not hoo:
            hoo = loc_dom.xpath(
                '//p[strong[contains(text(), "Opening hours:")]]/following-sibling::p/text()'
            )[:-1]
        hoo = (
            " ".join([e.strip() for e in hoo if e.strip()])
            .replace("Store opening hours", "")
            .strip()
            .split("SMÅLAND opening")[0]
            .split("(")[0]
            .strip()
            .split("Restaurant")[0]
            .strip()
        )
        if hoo.startswith(":"):
            hoo = hoo[1:]
        geo = loc_dom.xpath('//a[contains(@href, "maps/place")]/@href')
        latitude = ""
        longitude = ""
        if geo:
            geo = geo[0].split("/@")[-1].split(",")[:2]
            latitude = geo[0]
            longitude = geo[1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="ES",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=" ".join(raw_adr),
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
