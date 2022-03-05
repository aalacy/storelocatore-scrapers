from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.sweetchick.com/menu/"
    domain = "sweetchick.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//p[span[strong[u[contains(text(), "LOCATIONS")]]]]/following-sibling::p'
    )[:5]
    for poi_html in all_locations:
        raw_data = " ".join(
            [e.strip() for e in poi_html.xpath(".//text()") if e.strip()]
        )
        raw_address = raw_data.split("- ")[-1].split(", ")
        zip_code = raw_address[2].split()[-1]
        if len(zip_code) == 2:
            zip_code = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=raw_data.split("- ")[0].strip(),
            street_address=raw_address[0],
            city=raw_address[1],
            state=raw_address[2].split()[0],
            zip_postal=zip_code,
            country_code="",
            store_number="",
            phone="",
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation="<INACCESIBLE>",
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
