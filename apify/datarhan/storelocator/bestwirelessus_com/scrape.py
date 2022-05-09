from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.bestwirelessus.com/locations/"
    domain = "bestwirelessus.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@class, "gbcols_col") and h3]')
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//h3/text()")[0].strip()
        raw_data = poi_html.xpath('.//p[@class="gbcols_p"]/text()')
        raw_data = [e.strip() for e in raw_data if e.strip() and e != "&nbsp"]
        if not raw_data:
            continue
        phone = [e.split(":")[1] for e in raw_data if "Tel" in e]
        phone = phone[0].split(",")[0] if phone else ""
        if len(raw_data[1].split(", ")) == 3:
            zip_code = raw_data[1].split(", ")[2]
        else:
            zip_code = raw_data[1].split(", ")[1].split()[1]
        street_address = raw_data[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=raw_data[1].split(", ")[0],
            state=raw_data[1].split(", ")[1].split()[0],
            zip_postal=zip_code,
            country_code="",
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
