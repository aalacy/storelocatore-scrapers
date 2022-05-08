from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.ge/dealers/"
    domain = "toyota.ge"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="cmp-btn btn-primary"]/a/@href')
    for url in all_locations:
        page_url = urljoin(start_url, url)
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h2/text()")[0].strip()
        raw_address = (
            loc_dom.xpath('//b[contains(text(), "მის")]/following::text()')[0]
            .replace(".:", "")
            .strip()
            .split(", ")
        )
        phone = loc_dom.xpath('//p/a[contains(@href, "tel")]/text()')
        if not phone:
            phone = loc_dom.xpath(
                '//b[contains(text(), "ქოლ ცენტრი")]/following::text()'
            )
        phone = phone[0].replace(":", "").strip() if phone else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=", ".join(raw_address[2:]),
            city=raw_address[1],
            state="",
            zip_postal="",
            country_code=raw_address[0].replace(":", ""),
            store_number="",
            phone=phone,
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
