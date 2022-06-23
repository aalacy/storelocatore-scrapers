from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://ccmdcenters.com/locations"
    domain = "ccmdcenters.com"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Location Details")]/@href')
    for page_url in list(set(all_locations)):
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="entry-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//header[@class="entry-header"]/p/span/text()')[:2]
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if not raw_address:
            continue
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else ""
        geo = (
            loc_dom.xpath('//div[@class="location-map"]/a/img/@data-lazy-src')[0]
            .split("center=")[1]
            .split("&")[0]
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
        hoo = loc_dom.xpath("//header/p[2]//text()")
        hoo = [e.strip() for e in hoo]
        hours_of_operation = (
            " ".join(hoo).replace("TEMPORARY HOURS ", "") if hoo else ""
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number="",
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
