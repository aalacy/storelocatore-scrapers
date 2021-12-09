from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.razer.com/razerstores"
    domain = "razer.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[a[contains(text(), "Visit Store")]]')
    for poi_html in all_locations:
        url = poi_html.xpath('.//a[contains(text(), "Visit Store")]/@href')[0]
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        raw_data = loc_dom.xpath(
            '//h2[contains(text(), "LOCATION")]/following-sibling::div/text()'
        )
        if not raw_data:
            raw_data = loc_dom.xpath(
                '//h2[contains(text(), "交通位置")]/following-sibling::div/text()'
            )
        raw_data = [e.strip() for e in raw_data]
        location_name = loc_dom.xpath('//h1[@class="header"]/text()')[0]
        raw_address = poi_html.xpath("text()")
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = [e for e in raw_data if "+" in e][0].replace("Tel: ", "").strip()
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
            .split("ll=")[-1]
            .split("&")[0]
            .split(",")
        )
        if "@" in geo[0]:
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
        latitude = ""
        longitude = ""
        if len(geo) > 1:
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = loc_dom.xpath(
            '//strong[contains(text(), "Opening Hours")]/following::text()'
        )
        if not hours_of_operation:
            hours_of_operation = raw_data[1:]
        hoo = hours_of_operation[0].strip().split(" Hours: ")[-1]
        if "Friday" in hours_of_operation[1] or "Sunday" in hours_of_operation[1]:
            hoo += " " + hours_of_operation[1].strip()
        if "Sunday" in hours_of_operation[2]:
            hoo += " " + " ".join([e.strip() for e in hours_of_operation[1:3]])
        if "taipei" in store_url:
            hoo = " ".join([e for e in raw_data if " – 2" in e])

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
