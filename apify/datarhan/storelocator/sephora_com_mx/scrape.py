from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sephora.com.mx/stores/"
    domain = "sephora.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@id="stores"]/li')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h4/text()")[0]
        addr = parse_address_intl(poi_html.xpath("@data-address")[0])
        zip_code = poi_html.xpath("@data-zip")[0].strip()[:-1]
        street_address = poi_html.xpath("@data-address")[0].split(zip_code)[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        phone = poi_html.xpath('.//div[@class="store-phone"]/text()')[-1].strip()
        hoo = poi_html.xpath('.//div[@class="store-hours"]/text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        latitude = poi_html.xpath("@data-latitude")[0]
        if latitude == "null":
            latitude = ""
        longitude = poi_html.xpath("@data-longitude")[0]
        if longitude == "null":
            longitude = ""

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.sephora.com.mx/stores/",
            location_name=location_name,
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code="MX",
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hoo,
            raw_address=poi_html.xpath("@data-address")[0],
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
