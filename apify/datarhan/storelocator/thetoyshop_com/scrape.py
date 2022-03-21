import json
from lxml import etree
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "thetoyshop.com"
    start_url = "https://www.thetoyshop.com/store-finder"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath("//li/@data-url")
    all_locations = []
    for url in all_urls:
        reg_url = urljoin(start_url, url)
        data = session.get(reg_url).json()
        all_locations += data["data"]
        total = data["total"]
        if total > 10:
            pages = total // 10 + 1
            for p in range(1, pages):
                page_url = add_or_replace_parameter(reg_url, "page", str(p))
                data = session.get(page_url)
                if data.text:
                    data = json.loads(data.text)
                    all_locations += data["data"]

    for poi in all_locations:
        store_url = "https://www.thetoyshop.com" + poi["url"]
        location_name = poi["displayName"]
        if "Opening Soon" in location_name:
            continue
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["line1"]
        if poi["line2"]:
            street_address += " " + poi["line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["town"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for d, h in poi["openings"].items():
            hoo.append(f"{d} {h}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
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
