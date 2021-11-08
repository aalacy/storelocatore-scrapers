from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.xpresspa.com/Articles.asp?ID=262"
    domain = "xpresspa.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[h4[@class="location_state-city"]]')
    for poi_html in all_locations:
        state = poi_html.xpath(".//h4/text()")[0].split(" - ")[0]
        city = poi_html.xpath(".//h4/text()")[0].split(" - ")[-1]
        street_address = poi_html.xpath('.//p[@class="location_airport"]/text()')[0]
        street_address += ", " + poi_html.xpath(".//h5/text()")[0].strip()
        phone = poi_html.xpath(
            './/dt[contains(text(), "Telephone")]/following-sibling::dd/text()'
        )[0]
        hoo = poi_html.xpath(
            './/dt[contains(text(), "Hours")]/following-sibling::dd/text()'
        )[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name="",
            street_address=street_address,
            city=city,
            state=state,
            zip_postal="",
            country_code="",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
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
