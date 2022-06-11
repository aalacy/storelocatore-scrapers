from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota-trinidad.com/find-a-dealer/"
    domain = "toyota-trinidad.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[h2[contains(text(), "Office")]]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h2/text()")[0]
        raw_data = poi_html.xpath(".//p/text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        raw_address = " ".join(raw_data).split("Ph:")[0].strip()
        phone = poi_html.xpath(".//a/text()")[0]
        hoo = " ".join(raw_data).split("Hours: ")[-1].split("Service")[0].strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=raw_address.split(", ")[0],
            city=raw_data[1].split(", ")[-1].replace(".", ""),
            state="",
            zip_postal="",
            country_code="Trinidad and Tobago",
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
