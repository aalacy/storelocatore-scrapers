from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://imagestudios360.com/locations/"
    domain = "imagestudios360.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="locations_list_block"]/a/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="pro_title"]/text()')[0]
        raw_address = loc_dom.xpath('//div[@class="salon_address"]/text()')
        raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else ""
        city = addr.city
        if not city:
            city = location_name.split(",")[0]
        city = city if city else ""
        state = location_name.split(", ")[-1]
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else ""
        if len(zip_code) > 5:
            zip_code = ""
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = (
            phone[0].replace("Lori", "").replace("or Rich", "").split(" 781")[0]
            if phone and "@" not in phone[0]
            else ""
        )
        location_type = "<MISSING>"
        if "coming-soon" in page_url:
            continue
        if "COMING SOON" in location_name:
            continue

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
            location_type=location_type,
            latitude="",
            longitude="",
            hours_of_operation="",
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
