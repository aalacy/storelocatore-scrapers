import re
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "pizzastudio.com"
    start_url = "https://pizzastudio.com/stores.json"

    response = session.get(start_url)
    all_locations = json.loads(response.text)
    for poi in all_locations:
        if poi["comingsoon"] == 1:
            continue
        store_url = "https://pizzastudio.com/locations/" + poi["locationurl"]
        location_name = poi["locationname"].replace("&acirc;", "â")
        street_address = poi.get("address1")
        if not street_address and location_name == "St. John":
            street_address = "11 E Point Way"
        city = poi["city"]
        state = poi["stateabbrev"]
        if "," in city:
            state = city.split(",")[-1].strip()
            if "GO" in state:
                state = ""
            city = city.split(",")[0]
        zip_code = poi.get("zip")
        zip_code = str(zip_code) if zip_code else ""
        phone = poi.get("phone")
        latitude = poi.get("lat")
        longitude = poi.get("lon")
        hoo = ""
        if poi.get("hours"):
            hoo = etree.HTML(poi["hours"])
            if hoo:
                hoo = [elem.strip() for elem in hoo.xpath(".//text()") if elem.strip]
                hours_of_operation = (
                    " ".join(hoo).split("Start")[0] if hoo else "<MISSING>"
                )
                hours_of_operation = hours_of_operation.replace("Catering Options", "")
                hours_of_operation = (
                    hours_of_operation.split("Sign")[0]
                    .split("Click")[0]
                    .replace(" Delivery Available", "")
                )
                if "Re" in hours_of_operation:
                    hours_of_operation = re.findall(
                        "Re-Opening.+?: (.+)", hours_of_operation
                    )[0].replace("\xa0", " ")
        country_code = ""
        if len(zip_code) == 5:
            country_code = "US"
        if len(zip_code.split()) == 2:
            country_code = "CA"
        if "brazil" in store_url:
            country_code = "BR"
        if poi["comingsoon"] == 1:
            hours_of_operation = "Coming Soon"

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=country_code,
            store_number="",
            phone=phone,
            location_type="",
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
