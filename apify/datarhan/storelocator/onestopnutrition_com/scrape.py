from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://onestopnutrition.com/locations/"
    domain = "onestopnutrition.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="vc_row wpb_row vc_inner vc_row-fluid"]')
    for poi_html in all_locations:
        if not poi_html.xpath(".//h4/strong/text()"):
            continue
        store_url = start_url
        location_name = poi_html.xpath(".//h4/strong/text()")
        location_name = " ".join(location_name) if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="wpb_wrapper"]/p/text()')[:3]
        raw_address = [e.strip() for e in raw_address if e.strip()]
        if len(raw_address[-1].split("-")) == 3:
            raw_address = raw_address[:-1]
        if "am-" in raw_address[-1]:
            raw_address = raw_address[:-2]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//div[@class="wpb_wrapper"]/p/text()')
        if len(phone) < 4:
            continue
        phone = phone[3].strip()
        if "Monday" in phone:
            phone = poi_html.xpath('.//div[@class="wpb_wrapper"]/p/text()')[2].strip()
        if "Tuesday" in phone:
            phone = poi_html.xpath('.//div[@class="wpb_wrapper"]/p/text()')[1].strip()
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="wpb_wrapper"]/p/text()')[4:]
        if "Monday" not in hoo[0]:
            hoo = poi_html.xpath('.//div[@class="wpb_wrapper"]/p/text()')[3:]
        if "Monday" not in hoo[0]:
            hoo = poi_html.xpath('.//div[@class="wpb_wrapper"]/p/text()')[2:]
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
