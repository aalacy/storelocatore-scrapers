from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.sephora.gr/el/sephora-katasthmata?ajax=1&all=1"
    domain = "sephora.gr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text.encode("utf-8"))

    all_locations = dom.xpath("//marker")
    for poi_html in all_locations:
        store_number = poi_html.xpath("@id_store")[0]
        page_url = f"https://www.sephora.gr/el/store?storeid={store_number}"
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = " ".join(loc_dom.xpath('//div[@class="description"]//text()'))

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi_html.xpath("@name")[0],
            street_address=loc_dom.xpath('//div[@class="address"]/text()')[0],
            city=loc_dom.xpath('//div[@class="city"]/text()')[0],
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code="GR",
            store_number=store_number,
            phone=poi_html.xpath("@phone")[0],
            location_type=SgRecord.MISSING,
            latitude=poi_html.xpath("@lat")[0],
            longitude=poi_html.xpath("@lng")[0],
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
