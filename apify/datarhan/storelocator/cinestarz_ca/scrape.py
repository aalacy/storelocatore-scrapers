from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://cinestarz.ca/"
    domain = "cinestarz.ca"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="sub-menu"]/li/a/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        open_soon = loc_dom.xpath('//h2[contains(text(), "OPENING SOON!")]')
        if open_soon:
            continue
        location_name = loc_dom.xpath('//*[@class="vc_custom_heading"]/text()')[0]
        if location_name.lower() == "get in touch":
            location_name = loc_dom.xpath('//h1[@class="vc_custom_heading"]/text()')[0]
        raw_data = loc_dom.xpath(
            '//div[@id="contact"]//div[@class="wpb_wrapper"]/p/text()'
        )
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//div[contains(@id,"contact")]//div[@class="wpb_wrapper"]/p//text()'
            )
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//div[contains(@id,"contact")]//div[@class="wpb_wrapper"]/div//text()'
            )
            raw_data = [e.strip() for e in raw_data if e.strip()][:5]
        raw_data = [e.strip() for e in raw_data if e != "Infoline: "]
        raw_address = ", ".join(raw_data[:-1])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        if street_address == "#300 Ab":
            street_address = raw_address.split(", ")[0]
        geo = (
            loc_dom.xpath("//iframe/@src")[0].split("sll=")[-1].split("&")[0].split(",")
        )
        hoo = loc_dom.xpath('//p[contains(text(), "Monday ")]/text()')
        if not hoo:
            hoo = loc_dom.xpath(
                '//h2[contains(text(), "Hours:")]/following-sibling::table//text()'
            )
        if not hoo:
            hoo = loc_dom.xpath('//p[contains(text(), "Weekdays:")]/text()')
        hoo = (
            " ".join([e.strip() for e in hoo if e.strip()])
            .split("*")[0]
            .replace("Day Opening Closing ", "")
            .strip()
        )
        state = addr.state
        if state and state.endswith("."):
            state = state[:-1]
        temp_closed = loc_dom.xpath('//img[contains(@src, "EMPORARILYCLOSED")]')
        location_type = ""
        if temp_closed:
            location_type = "temporarily closed"

        if len(geo) == 1:
            geo = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("!2d")[-1]
                .split("!2m3")[0]
                .split("!3d")[::-1]
            )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=state,
            zip_postal=addr.postcode,
            country_code="CA",
            store_number="",
            phone=raw_data[-1].split(":")[-1].strip(),
            location_type=location_type,
            latitude=geo[0],
            longitude=geo[1],
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
