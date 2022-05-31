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
    domain = "fitnessfirst.co.uk"
    start_url = "https://www.fitnessfirst.co.uk/Umbraco/Api/Club/GetClubs?facilities=&classes=&location=&regions=&subRegions="

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        store_number = poi["id"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        location_name = poi["name"]
        page_url = urljoin(start_url, poi["url"])
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        data = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')
        if data:
            poi_data = json.loads(data[0])
            poi_data = [e for e in poi_data if e["@type"] == "ExerciseGym"][0]
            street_address = poi_data["address"]["streetAddress"]
            city = poi_data["address"]["addressLocality"]
            zip_code = poi_data["address"]["postalCode"]
            country_code = poi_data["address"]["addressCountry"]
            phone = poi_data["telephone"]
            location_type = poi_data["@type"]
        else:
            raw_address = loc_dom.xpath("//address/text()")[0]
            street_address = ", ".join(raw_address.split(",")[:2])
            city = raw_address.split(",")[-2]
            zip_code = raw_address.split(",")[-1]
            country_code = "GB"
            phone = loc_dom.xpath(
                '//span[contains(text(), "Phone")]/following-sibling::span/text()'
            )[0]
            location_type = ""
        hoo = loc_dom.xpath('//div[@class="opening-hours order-md-1"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()]).split("More")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
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
