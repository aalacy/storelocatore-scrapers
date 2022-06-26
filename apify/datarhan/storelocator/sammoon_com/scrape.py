from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://sammoon.com/pages/locations"
    domain = "sammoon.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div/table")
    for poi_html in all_locations:
        location_name = poi_html.xpath(".//td/h3/text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_data = poi_html.xpath(".//tr[1]/td[1]/p[1]/text()")
        if len(raw_data) == 4:
            raw_data = [" ".join(raw_data[:2])] + raw_data[2:]
        street_address = raw_data[0][:-1]
        city = raw_data[1].split(", ")[0]
        state = raw_data[1].split(", ")[-1].split()[0]
        zip_code = raw_data[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[-1].split(":")[-1].strip()
        location_type = "<MISSING>"
        geo = poi_html.xpath(".//following-sibling::iframe[1]/@src")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            geo = geo[0].split("!2d")[-1].split("!2m")[0].split("!3d")
            latitude = geo[-1]
            longitude = geo[0]
        hoo = poi_html.xpath(".//tr[1]/td[1]/p[2]//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=start_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
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
