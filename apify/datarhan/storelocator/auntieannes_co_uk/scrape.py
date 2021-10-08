import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "auntieannes.co.uk"
    start_url = "https://www.auntieannes.co.uk/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "mapsvg_options")]/text()')[0]
    data = re.findall("mapsvg_options =(.+);jQuery", data)[0]
    data = json.loads(data)

    for poi in data["options"]["data_objects"]["objects"]:
        store_url = start_url
        location_name = poi["store_name"]
        addr = parse_address_intl(poi["location"]["address"]["formatted"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = poi["location"]["address"].get("postal_town")
        if not city:
            city = poi["location"]["address"]["locality"]
        state = poi["location"]["address"].get("administrative_area_level_2")
        if not state:
            state = poi["location"]["address"]["administrative_area_level_1"]
        state = state if state else "<MISSING>"
        zip_code = poi["location"]["address"].get("postal_code")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["address"]["country_short"]
        store_number = poi["id"]
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["geoPoint"]["lat"]
        longitude = poi["location"]["geoPoint"]["lng"]
        hoo = []
        if poi["opening_hours"]:
            hoo = etree.HTML(poi["opening_hours"]).xpath("//text()")
        hoo = [e.strip() for e in hoo if e.strip()]
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
