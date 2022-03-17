from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.qshop.us/"
    domain = "qshop.us"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@role="row"]/div[@role="gridcell"]')
    for poi_html in all_locations:
        raw_data = poi_html.xpath('.//div/p[@class="font_2"]//text()')
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if len(raw_data) > 5:
            raw_data = raw_data[:3] + [" ".join(raw_data[3:5])] + raw_data[5:]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=raw_data[0],
            street_address=raw_data[2],
            city=raw_data[3].split(", ")[0],
            state=raw_data[3].split(", ")[-1].split()[0],
            zip_postal=raw_data[3].split(", ")[-1].split()[-1],
            country_code="",
            store_number=raw_data[1].split("#")[-1],
            phone=raw_data[-1],
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="",
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
