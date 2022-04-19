from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sweetchick.com/"
    domain = "sweetchick.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//button[contains(text(), "Locations")]/following-sibling::div[1]//a/@href'
    )
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = page_url.split("/")[-2].replace("-", " ").title()
        raw_address = loc_dom.xpath('//a[@data-bb-track-label="Location"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        hoo = loc_dom.xpath('//p[contains(text(), "Brunch")]/text()')
        hoo += loc_dom.xpath('//p[contains(text(), "Lunch ")]/text()')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=raw_address[0],
            city=raw_address[1].split(", ")[0],
            state=raw_address[1].split(", ")[1].split()[0],
            zip_postal=raw_address[1].split(", ")[1].split()[1],
            country_code="",
            store_number="",
            phone="",
            location_type="",
            latitude=loc_dom.xpath("//@data-gmaps-lat")[0],
            longitude=loc_dom.xpath("//@data-gmaps-lng")[0],
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
