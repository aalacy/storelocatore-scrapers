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

    start_url = "https://www.tascoautocolor.com/store-locations.html#/"
    domain = "tascoautocolor.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//h2/following-sibling::div[@class="paragraph"][1]')[1:]
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//preceding-sibling::h2[1]//text()")[0]
        raw_address = poi_html.xpath(
            './/strong[span[contains(text(), "Location")]]/following::text()'
        )
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if raw_address and len(raw_address[0].split(", ")) > 2:
            raw_address = raw_address[0].strip().split(", ") if raw_address else ""
        else:
            raw_address = (
                ", ".join(raw_address[:2]).strip().split(", ") if raw_address else ""
            )
        if not raw_address:
            raw_address = poi_html.xpath("text()")
            if raw_address and len(raw_address[-1].split(", ")) > 2:
                raw_address = raw_address[-1].strip().split(", ") if raw_address else ""
            else:
                raw_address = (
                    ", ".join(raw_address[-2:]).strip().split(", ")
                    if raw_address
                    else ""
                )
        if not raw_address:
            raw_address = poi_html.xpath(
                './/*[contains(text(), "Location:")]/following::text()'
            )
            raw_address = [
                e.strip() for e in raw_address if e.strip() and e.strip() != ">"
            ]
            if raw_address and len(raw_address[0].split(", ")) > 1:
                raw_address = (
                    ", ".join(raw_address).strip().split(", ") if raw_address else ""
                )
                if len(raw_address) == 2:
                    raw_address = [raw_address[0]] + raw_address[1].split(", ")
            else:
                raw_address = (
                    ", ".join(raw_address[:2]).strip().split(", ")
                    if raw_address
                    else ""
                )
        raw_address = [e.strip() for e in raw_address if not e.startswith("(")]
        phone = poi_html.xpath(
            './/strong[contains(text(), "Phone:")]/following::text()'
        )
        phone = [e.strip() for e in phone if e.strip()]
        phone = phone[0].strip() if phone else ""
        if not phone:
            phone = [e.strip() for e in raw_address if e.startswith("(")]
            phone = phone[0] if phone else ""
        if not phone:
            phone = poi_html.xpath("text()")
            phone = phone[0] if phone else ""
        if not phone:
            raw_data = poi_html.xpath(".//span/text()")
            raw_data = [e.strip() for e in raw_data if e.strip() and "(" in e]
            phone = raw_data[0] if raw_data else ""
        if phone:
            phone = phone.split(",")[0].strip()
        raw_address = (
            ", ".join(raw_address)
            .split(", Shop")[0]
            .split(", Tasco Auto Color")[0]
            .strip()
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        store_number = (
            location_name.split("#")[-1].split("-")[0].strip()
            if "#" in location_name
            else ""
        )
        latitude = ""
        longitude = ""
        geo = poi_html.xpath('.//a[contains(@href, "maps")]/@href')
        if geo and len(geo) > 1:
            geo = geo[0].split("ll=")[-1].split("&")[0].split(",")
            latitude = geo[0]
            longitude = geo[1]
        hoo = poi_html.xpath('.//strong[contains(text(), "Hours:")]/following::text()')
        hoo = hoo[0] if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code="",
            store_number=store_number,
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
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
