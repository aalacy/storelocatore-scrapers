from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com/sg/en/stores/"
    domain = "ikea.com/sg"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[@class="pub__btn pub__btn--small pub__btn--primary"]/@href'
    )
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")[0]
        hoo = loc_dom.xpath(
            '//h2[strong[contains(text(), "Store opening hours")]]/following-sibling::p//text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h2[contains(text(), "Store opening hours")]/following-sibling::p//text()'
            )
        if not hoo:
            hoo = dom.xpath(
                '//div[div[h2[contains(text(), "{}")]]]/following-sibling::div[1]//h3[strong[contains(text(), "STORE OPENING HOURS")]]/following-sibling::p[1]//text()'.format(
                    location_name
                )
            )
        hoo = " ".join(hoo)
        geo = loc_dom.xpath('//a[contains(text(), "View full map")]/@href')
        phone = ""
        street_address = ""
        city = ""
        zip_code = ""
        latitude = ""
        longitude = ""
        if geo:
            geo = geo[0].split("@")[-1].split(",")
            latitude = geo[0]
            longitude = geo[1]
            raw_address = (
                loc_dom.xpath('//a[contains(text(), "View full map")]/@href')[0]
                .split("daddr=")[-1]
                .split("@")[0]
                .replace("+", " ")
                .replace(location_name, "")
                .strip()
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address = ", " + addr.street_address_2
            if "google.com" in street_address.lower():
                street_address = ""
            zip_code = addr.postcode
            city = addr.city
            phone = dom.xpath('//a[contains(@href, "tel")]/text()')[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="SG",
            store_number="",
            phone=phone,
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
