from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://sparnigeria.com/store-locations/"
    domain = "sparnigeria.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[figure[@class="fancy-box-image"]]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")[0]
        raw_data = poi_html.xpath('.//span[@class="trainer"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = raw_data[0].replace("Add: ", "")
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        geo = poi_html.xpath(".//a/@href")[0].split("/@")[-1].split(",")[:2]
        zip_code = addr.postcode
        if zip_code == "YABA":
            zip_code = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code=addr.country,
            store_number="",
            phone=raw_data[1].replace("Phone : ", ""),
            location_type="",
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation="",
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
