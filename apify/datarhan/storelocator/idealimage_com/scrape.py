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
    domain = "idealimage.com"
    start_url = "https://www.idealimage.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang="

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//store/item")
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//exturl/text()")[0]
        store_url = urljoin("https://www.idealimage.com", store_url)
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)
        location_name = poi_html.xpath(".//location/text()")
        location_name = (
            location_name[0].replace("amp;", "") if location_name else "<MISSING>"
        )
        addr = parse_address_intl(poi_html.xpath(".//address/text()")[0])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if not street_address:
            addr = parse_address_intl(
                " ".join(loc_dom.xpath('//div[@class="centeraddress"]//text()')[1:3])
            )
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
        country_code = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/@href')
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        store_number = poi_html.xpath(".//storeid/text()")[0]
        latitude = poi_html.xpath(".//latitude/text()")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath(".//longitude/text()")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//table[@class="tbl-hours"]//text()')
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
