import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_usa


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
    start_url = "https://wbliquors.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[contains(@class, "jet-listing-grid__item jet-listing-dynamic-post-") and @data-post-id]'
    )
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h5/text()")[0].replace("\n", "").strip()
        raw_addr = poi_html.xpath(
            './/div[@class="elementor-widget-container"]/p/text()'
        )[0]
        addr = parse_address_usa(raw_addr)
        city = addr.city
        if not city and len(raw_addr.split(", ")) > 1:
            city = raw_addr.split(", ")[1]

        street_address = raw_addr.rsplit(city, 1)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        if not city:
            street_address = raw_addr
        if city and ", " in city:
            street_address += ", " + city.split(", ")[0]
            city = city.split(", ")[-1]
        if len(street_address.split()) == 1:
            street_address = raw_addr.split(", ")[0]
        if city and street_address.endswith(city):
            street_address = street_address[: len(city)].strip()
        state = addr.state
        zip_code = addr.postcode
        country_code = addr.country
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/span/text()')
        phone = phone[0] if phone else SgRecord.MISSING
        hoo = poi_html.xpath('.//p[contains(text(), "Monday")]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
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
