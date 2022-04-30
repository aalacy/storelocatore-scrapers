import re
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
    response = session.get("https://locations.penningtons.com/en")
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "REDUX_STATE__ = ")]/text()')[0]
    data = re.findall("REDUX_STATE__ = (.+);", data)[0]
    data = json.loads(data)
    all_ids = [
        str(e["properties"]["id"])
        for e in data["dataLocations"]["collection"]["features"]
    ]

    start_url = "https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/Lq80oSBFP79mUqPqs3toQ2RqHFrAzm/locations-details?locale=en_CA&ids={}&clientId=5fc54808ae5334a2323b2de2&cname=locations.penningtons.com"
    domain = "penningtons.com"
    response = session.get(start_url.format(",".join(all_ids)))
    data = json.loads(response.text)

    for poi in data["features"]:
        store_url = urljoin(
            "https://locations.penningtons.com/", poi["properties"]["slug"]
        )
        location_name = poi["properties"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["properties"]["addressLine1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["properties"]["city"]
        city = city if city else "<MISSING>"
        state = poi["properties"]["province"]
        zip_code = poi["properties"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["properties"]["country"]
        store_number = poi["properties"]["branch"]
        phone = poi["properties"]["phoneLabel"]
        location_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][-1]
        longitude = poi["geometry"]["coordinates"][0]
        hoo = []
        for day, hours in poi["properties"]["hoursOfOperation"].items():
            opens = hours[0][0]
            closes = hours[0][1]
            hoo.append(f"{day} {opens} {closes}")
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
