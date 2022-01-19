from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.goldmansachs.com/our-firm/locations.html"
    domain = "goldmansachs.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="listings filter"]/li')
    for poi_html in all_locations:
        country_code = poi_html.xpath('.//span[@class="country"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_url = start_url
        location_name = poi_html.xpath('.//span[@class="address"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//span[@class="address"]/text()')[1:]
        raw_address = [e.strip() for e in raw_address if e.strip()]
        full_address = " ".join(raw_address) + " " + country_code
        addr = parse_address_intl(full_address)
        if not addr.street_address_1:
            raw_address = poi_html.xpath('.//span[@class="address"]/text()')
            location_name = "<MISSING>"
            addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if street_address and addr.street_address_2:
            street_address += " " + addr.street_address_2
        else:
            street_address = addr.street_address_2
        if not street_address:
            if country_code in ["Canada", "United Kingdom"]:
                street_address = ", ".join(raw_address[:2])
            else:
                street_address = raw_address[0]
        city = poi_html.xpath('.//span[@class="city"]/text()')
        city = city[0].split(",")[0] if city else "<MISSING>"
        state = addr.state
        state = state.replace(".", "") if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        street_address = street_address.replace(zip_code, "")
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//span[@class="phone"]/span/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        if street_address == "Suite 1000 East":
            street_address = f"{location_name} {street_address}"
            location_name = "<MISSING>"

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
            raw_address=full_address,
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
