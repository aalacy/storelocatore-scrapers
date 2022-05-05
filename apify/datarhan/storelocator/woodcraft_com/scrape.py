from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "woodcraft.com"
    start_url = "https://www.woodcraft.com/store_locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="stores-by-state__store-link"]/@href')
    for page_url in all_locations:
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//p[@itemprop="address"]/text()')
        raw_address = ", ".join([elem.strip() for elem in raw_address if elem.strip()])
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        if "This Store Is Now Closed" in street_address:
            continue
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else ""
        hours_of_operation = loc_dom.xpath(
            '//table[@class="table table--hours"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation).replace("Please Wear Mask", "")
            if hours_of_operation
            else ""
        )
        hours_of_operation = (
            hours_of_operation.replace(" Face mask required.", "")
            .replace("\n", "")
            .replace("Face Mask Required", "")
            .replace("Masks Required", "")
            .replace("Mask required", "")
            .replace("Face Masks Strongl", "")
            .replace("Face Masks Strong", "")
        )
        hours_of_operation = (
            hours_of_operation.replace("Face Masks Strong ", "")
            .replace("Face Mask Require", "")
            .replace("masks required", "")
            .replace("Open to the public", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace("\r", "")
            .replace("Face Mask Requi", "")
        )

        str_to_del = [
            "Shoppes of New Castle ",
            "Parkway Shopping Center ",
            "Overland Park Shopping Center ",
            "Tri-County Towne Center ",
            "Battlefield Shopping Center ",
            "Hunnington Place, ",
            "Shoppes of New Castle ",
            "Towne Square Shopping Center Next to Sams ",
            "Ravensworth Shopping Center ",
            "Henrietta Plaza ",
        ]
        for elem in str_to_del:
            street_address = street_address.replace(elem, "")
        street_address = street_address.split(", use")[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
