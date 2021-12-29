from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://waybackburgers.com/locations/"
    domain = "waybackburgers.com"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//li[@class="location-info-wrapper"]/h3/a/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url, headers=hdr)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="location-name"]/text()')[0]
        raw_address = loc_dom.xpath('//div[@class="location-address"]/text()')[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="location-phone"]/a[2]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        if loc_dom.xpath('//div[@class="coming-soon"]'):
            location_type = "coming soon"
        latitude = loc_dom.xpath("//@data-markerlat")[0]
        longitude = loc_dom.xpath("//@data-markerlon")[0]
        hoo_data = loc_dom.xpath('//div[@class="location-hours"]/ul//text()')
        hoo_data = [e.strip() for e in hoo_data if e.strip()]
        days = hoo_data[:7]
        hours = hoo_data[7:]
        hoo = list(map(lambda d, h: d + " " + h, days, hours))
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
