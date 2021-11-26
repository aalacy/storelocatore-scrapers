import re
import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "sanrio.com"
    start_url = "https://cdn.shopify.com/s/files/1/0416/8083/0620/t/161/assets/sca.storelocator_scripttag.js?v=1629914766&shop=sanrio-na.myshopify.com"

    response = session.get(start_url)
    data = re.findall("Setting=(.+);", response.text)[0]
    data = data.split("locationsRaw:")[-1][1:].split("'},function")[0]
    all_locations = json.loads(data)

    for poi in all_locations:
        store_url = "https://www.sanrio.com/pages/store-locator"
        location_name = poi["name"]
        street_address = poi["address"]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["postal"]
        country_code = "US"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = poi.get("schedule")
        if hoo:
            if "<br>" in hoo:
                hoo = hoo.split("<br>")
                hoo = hoo[0][:-2] + " " + hoo[1]

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
