from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.awrestaurants.com.sg/locations"
    domain = "awrestaurants.com.sg"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location-block"]')
    for poi_html in all_locations:
        raw_data = poi_html.xpath(".//p/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if "Centre" in raw_data[2]:
            raw_data = [" ".join(raw_data[:2])] + raw_data[2:]
        street_address = " ".join(raw_data[:2]).replace(
            " Jurong Point Shopping Centre", ""
        )
        city = raw_data[2].split()[0]
        zip_code = raw_data[2].split()[-1]
        hoo = poi_html.xpath('.//div[@class="location-block-btns"]//li/text()')
        if not hoo:
            hoo = poi_html.xpath('.//div[@class="location-block-btns"]/p/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).split(zip_code)[-1].strip() if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name="",
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone="",
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
