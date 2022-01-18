# -*- coding: utf-8 -*-
import re
import yaml

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.barbour.com/storelocator"
    domain = "barbour.com"

    response = session.get(start_url)
    data = re.findall(r"amLocator\((.+)\);", response.text.replace("\n", ""))[0]
    data = yaml.load(data.split(");    });</script>")[0], Loader=yaml.FullLoader)

    for poi in data["jsonLocations"]["items"]:
        location_name = poi["name"]
        street_address = poi["address"]
        street_address = (
            street_address.replace("?", "").strip() if street_address else ""
        )
        if street_address == "-":
            street_address = ""
        if street_address:
            street_address = " ".join(street_address.split())
        city = poi["city"]
        if city:
            city = city.replace("?", "")
        state = poi["state"]
        if state and state.isdigit():
            state = ""
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        location_type = "<MISSING>"
        if poi["attributes"].get("stockist_type", {}).get("option_title"):
            location_type = poi["attributes"]["stockist_type"]["option_title"][0]
        latitude = poi["lat"]
        if latitude == "0.00000000":
            latitude = ""
        longitude = poi["lng"]
        if longitude == "0.00000000":
            longitude = ""

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
            hours_of_operation="",
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.COUNTRY_CODE})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
