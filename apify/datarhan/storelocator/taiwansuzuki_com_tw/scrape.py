from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.taiwansuzuki.com.tw/locator.php"
    domain = "taiwansuzuki.com.tw"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//select[@id="city"]/option/@value')
    for city in all_cities:
        url = f"https://www.taiwansuzuki.com.tw/locator.php?type=1&city={city}"
        response = session.get(url, headers=hdr)
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//ul[@class="locatorBox"]/li')
        for poi_html in all_locations:
            location_name = poi_html.xpath(".//div/h3/text()")[0].strip()
            raw_address = poi_html.xpath('.//p[@class="address"]/text()')[0].strip()
            hoo = poi_html.xpath('.//p[@class="time"]/text()')[0]
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')[0]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state="",
                zip_postal=addr.postcode,
                country_code="TW",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
                hours_of_operation=hoo,
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
