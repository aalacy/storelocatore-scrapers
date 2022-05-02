from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests(proxy_country="us")
    domain = "katespade.com"
    start_url = "https://www.katespade.com/international-stores/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="see-in-shop"]/div[@class="vcard"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")[0]
        raw_data = poi_html.xpath(".//span/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        phone = [e for e in raw_data if e.startswith("+")]
        phone = phone[0] if phone else ""
        raw_address = " ".join(
            [e.strip() for e in raw_data if e.strip() and not e.startswith("+")]
        )
        if not raw_address:
            raw_address = location_name
            raw_address = " ".join(
                [
                    e.strip()
                    for e in raw_address.split()
                    if e.strip() and not e.startswith("+")
                ]
            )
        if phone:
            raw_address = raw_address.replace(phone, "").strip()
        if "royal caribbean" in raw_address:
            continue
        if len(raw_address.split()) < 4:
            continue
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if street_address and addr.street_address_2:
            street_address += ", " + addr.street_address_2
        else:
            street_address = addr.street_address_2
        country_code = addr.country
        if not country_code:
            country_code = poi_html.xpath(".//preceding-sibling::div[h2][1]/@id")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
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
            raw_address=raw_address.replace("\n", "")
            .replace("\t", "")
            .replace("\r", ""),
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
