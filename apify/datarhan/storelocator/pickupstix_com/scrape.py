import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "pickupstix.com"
    start_url = "https://www.pickupstix.com/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.post(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="all-locations"]//div/a[h4]/@href')

    for store_url in all_locations:
        store_url = urljoin(start_url, store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "geo")]/text()'
        )[0]
        poi = json.loads(poi.replace("\n", "").replace("\t", ""))

        location_name = poi["name"]
        street_address = poi["address"]["streetAddress"]
        city = poi["address"]["addressLocality"].strip()
        state = poi["address"]["addressRegion"].strip()
        zip_code = poi["address"]["postalCode"]
        phone = poi["telephone"]
        country_code = poi["address"]["addressCountry"]
        store_number = "<MISSING>"
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        hours_of_operation = " ".join(poi["openingHours"].split())

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
