from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "jaguar.co.uk"
    start_url = "https://www.jaguar.co.uk/retailers/retailer-opening-information.html"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//th[@class="tg-yseo"]/a/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1/span/text()')
        location_name = location_name[0] if location_name else ""
        if "PAGE NOT FOUND" in location_name:
            continue
        street_address = loc_dom.xpath(
            '//span[@class="retailerContact__address1"]/text()'
        )
        street_address = street_address[0] if street_address else ""
        street_2 = loc_dom.xpath('//span[@class="retailerContact__address2"]/text()')
        if street_2:
            street_address += " " + street_2[0]
        street_3 = loc_dom.xpath('//span[@class="retailerContact__address3"]/text()')
        if street_3:
            street_address += " " + street_3[0]
        street_address = street_address if street_address else ""
        city = loc_dom.xpath('//span[@class="retailerContact__locality"]/text()')
        city = city[0] if city else ""
        zip_code = loc_dom.xpath('//span[@class="retailerContact__postcode"]/text()')
        zip_code = zip_code[0] if zip_code else ""
        country_code = "UK"
        store_number = ""
        phone = loc_dom.xpath('//a[@class="tel"]/text()')
        phone = phone[0] if phone else ""
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else ""
        longitude = loc_dom.xpath("//@data-long")
        longitude = longitude[0] if longitude else ""
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "SALES OPENING TIMES")]/following-sibling::table//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type="",
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
