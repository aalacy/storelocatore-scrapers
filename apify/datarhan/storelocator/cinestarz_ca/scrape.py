import re
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://cinestarz.ca/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(text(), "Theaters")]/following-sibling::ul[1]//a/@href'
    )
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@class="vc_custom_heading"]/text()')[0]
        if "Get" in location_name:
            location_name = loc_dom.xpath("//h1/text()")[0]
        raw_data = loc_dom.xpath(
            '//div[contains(@id, "contact")]//div[@class="wpb_wrapper"]/*/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if raw_data[-1].lower() == "get in touch":
            raw_data = raw_data[:-1]
        if "cine starz" in raw_data[0].lower():
            raw_data = raw_data[1:]
        addr = parse_address_intl(" ".join(raw_data[:-1]))
        street_address = raw_data[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = addr.city
        state = addr.state
        if state.endswith("."):
            state = state[:-1]
        zip_code = addr.postcode.split("PHONE")[0].strip()
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1].split(":")[-1].strip()
        if not phone:
            phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0]
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[0].split("ll=")[-1].split("&")[0].split(",")
        )
        if len(geo) == 2:
            latitude = geo[0]
            longitude = geo[1]
        else:
            geo = (
                loc_dom.xpath("//iframe/@src")[0]
                .split("!2d")[-1]
                .split("!2m")[0]
                .split("!3d")
            )
            latitude = geo[1]
            longitude = geo[0]
        hoo = loc_dom.xpath(
            '//h3[strong[contains(text(), "Our doors")]]/following-sibling::p//text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h2[contains(text(), "Hours:")]/following-sibling::p[1]/text()'
            )
            if len(hoo) == 1:
                hoo = []
        if len(hoo) > 5:
            hoo = hoo = loc_dom.xpath(
                '//h1[@class="vc_custom_heading"]/following-sibling::div[2]//h3[strong[contains(text(), "Our doors")]]/following-sibling::p//text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//p[strong[contains(text(), "Hours:")]]/following-sibling::p[1]/text()'
            )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h3[small[contains(text(), "Our Doors are open:")]]/following-sibling::p[1]/text()'
            )
        hoo = [e.strip() for e in hoo if e.strip()]
        if not hoo:
            hoo = loc_dom.xpath(
                '//h2[contains(text(), "Hours:")]/following-sibling::table//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hoo = hoo[3:]
        hours_of_operation = (
            " ".join(hoo).split("*Weekend")[0].strip() if hoo else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
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
