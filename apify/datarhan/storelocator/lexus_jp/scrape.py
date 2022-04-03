import re
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://lexus.jp/dealership/"
    domain = "lexus.jp"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_regions = dom.xpath('//p[@class="ds-selectArea_btn"]/a/@href')
    for url in all_regions:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//li[@class="ds-dealer_detail"]')
        for poi_html in all_locations:
            url = poi_html.xpath('.//a[@class="ds-dealer_link"]/@href')[0]
            page_url = urljoin(start_url, url)
            location_name = poi_html.xpath('.//dt[@class="ds-dealer_name"]/text()')[0]
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)
            raw_address = loc_dom.xpath(
                '//dt[contains(text(), "住所")]/following-sibling::dd/text()'
            )
            raw_address = [e.strip() for e in raw_address]
            addr = parse_address_intl(raw_address[-1])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            zip_code = loc_dom.xpath('//span[@class="postal"]/text()')[0]
            phone = loc_dom.xpath(
                '//dt[contains(text(), "電話番号")]/following-sibling::dd/text()'
            )
            phone = phone[0].strip() if phone else ""
            store_number = poi_html.xpath("@data-dealercode")[0]
            hoo = loc_dom.xpath(
                './/dt[contains(text(), "営業時間")]/following-sibling::dd/text()'
            )[0]
            latitude = re.findall("latitude = '(.+?)';", loc_response.text)[0]
            longitude = re.findall("longitude = '(.+?)';", loc_response.text)[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=zip_code,
                country_code="JP",
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hoo,
                raw_address=raw_address[-1],
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
