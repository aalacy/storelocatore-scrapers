from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.acmedistribution.com/warehouse-locations/"
    domain = "acmedistribution.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="my-3" and h3]')
    for poi_html in all_locations:
        raw_address = poi_html.xpath(
            './/h3[contains(text(), "Address")]/following-sibling::p[1]/text()'
        )[0].split(", ")
        street_address = raw_address[0]
        city = raw_address[1]
        state = " ".join(raw_address[2].split()[:-1])
        zip_code = raw_address[2].split()[-1]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        hoo = poi_html.xpath(
            './/h4[contains(text(), "Hours")]/following-sibling::p[1]/text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).replace("Office Hours: ", "") if hoo else "<MISSING>"
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name="",
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
