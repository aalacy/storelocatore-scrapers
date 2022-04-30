from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests(verify_ssl=False)
    domain = "pizzastudiocanada.com"
    start_url = "https://pizzastudiocanada.com/home.html#locations"

    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//div[@class="column province"]')
    for state_html in all_states:
        state = state_html.xpath(".//h1/text()")[0]
        locations = state_html.xpath('.//div[@class="row"]')

        for poi_html in locations:
            store_url = "https://pizzastudiocanada.com/home.html#locations"
            location_name = poi_html.xpath(".//h2/text()")[0]
            street_address = poi_html.xpath('.//div[@class="column store"]/p/text()')[0]
            city = location_name
            zip_code = poi_html.xpath('.//div[@class="column store"]/p/text()')[-1]
            phone = poi_html.xpath('.//a[@class="telephone fb-track-lead"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            hoo = poi_html.xpath('.//table[@class="hours"]//text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = " ".join(hoo) if hoo else ""

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code="CA",
                store_number="",
                phone=phone,
                location_type="",
                latitude="",
                longitude="",
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
