import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.smartstartcanada.ca/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_states = dom.xpath(
        '//div[@id="cssmenu"]//a[contains(text(), "Locations")]/following-sibling::ul//a/@href'
    )[:-1]
    for url in all_states:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//h3[strong[contains(text(), "Locations")]]/following-sibling::ol/li'
        )

        for poi_html in all_locations:
            page_url = poi_html.xpath(".//strong/a/@href")[0]
            location_name = poi_html.xpath(".//strong/a/text()")[0]
            raw_address = poi_html.xpath("text()")

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=raw_address[0],
                city=raw_address[1].split(", ")[0],
                state=raw_address[1].split(", ")[-1],
                zip_postal=raw_address[-1],
                country_code="CA",
                store_number="",
                phone="",
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
