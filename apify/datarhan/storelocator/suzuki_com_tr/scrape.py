from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.suzuki.com.tr/tr/otomobil/yetkili-saticilar.html"
    domain = "suzuki.com.tr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="accordion"]/div[@class="card mt-2"]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(
            './/div[contains(@class, "card-header")]/p/text()'
        )[0]
        raw_address = poi_html.xpath(
            './/div[i[@class="fa fa-map-marker font-24 fa-fw mr-1 text-darkgrey"]]/p/text()'
        )[0]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = poi_html.xpath(
            './/div[i[@class="fa fa-phone font-24 fa-fw mr-1 text-darkgrey"]]/p/text()'
        )[0]
        city = addr.city
        if city:
            city = city.split("/")[-1]
        if not city:
            if "/" in raw_address:
                city = raw_address.split("/")[-1]
            else:
                city = raw_address.split(" - ")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="TR",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
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
