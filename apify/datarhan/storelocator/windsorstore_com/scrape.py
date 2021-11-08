import json
from lxml import etree
from urllib.parse import urljoin, unquote

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "windsorstore.com"
    start_url = (
        "https://cdn.shopify.com/s/files/1/0070/8853/7651/t/8/assets/stores.json"
    )

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["features"]:
        store_url = urljoin(
            "https://www.windsorstore.com/pages/locations", poi["properties"]["url"]
        )
        store_url = "".join(store_url.split())
        location_name = poi["properties"]["name"]
        if location_name == "zebra test location":
            continue
        if "Coming" in location_name:
            continue
        street_address = poi["properties"]["street_1"]
        if poi["properties"]["street_2"]:
            street_address += ", " + poi["properties"]["street_2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["properties"]["city"]
        state = poi["properties"]["state"]
        zip_code = poi["properties"]["zip"]
        country_code = "<MISSING>"
        store_number = poi["properties"]["store_number"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["properties"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geometry"]["coordinates"][-1]
        longitude = longitude if longitude else "<MISSING>"

        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        hours_of_operation = store_dom.xpath(
            '//div[@class="StoreDetail__hours"]/@data-store-hours'
        )
        hours_of_operation = (
            unquote(hours_of_operation[0]) if hours_of_operation else ""
        )
        hoo = []
        if hours_of_operation:
            hours_of_operation = json.loads(hours_of_operation)
            hours_of_operation = hours_of_operation if hours_of_operation else []
            for elem in hours_of_operation:
                hoo.append(f'{elem["day"]} {elem["hours"]}')
        hours_of_operation = " ".join(hoo).replace("+", " ") if hoo else "<MISSING>"

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
