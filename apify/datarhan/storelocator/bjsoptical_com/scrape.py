import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "bjsoptical.com"
    start_url = "https://api.bjs.com/digital/live/api/v1.2/club/search/10201"
    headers = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    body = '{"Town":"","latitude":"40.75368539999999","longitude":"-73.9991637","radius":"50000","zipCode":""}'
    response = session.post(start_url, data=body, headers=headers)
    data = json.loads(response.text)

    for poi in data["Stores"]["PhysicalStore"]:
        coming_soon = [
            elem["value"] for elem in poi["Attribute"] if elem["name"] == "Coming Soon"
        ][0]
        if coming_soon == "Yes":
            continue
        location_name = poi["Description"][0]["displayStoreName"]
        store_url = f"https://www.bjs.com/cl/{location_name.lower()}/{poi['storeName']}"
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["addressLine"][0]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["stateOrProvinceName"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code.strip() if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeName"]
        phone = poi.get("telephone1")
        phone = phone.strip() if phone else "<MISSING>"
        location_type = [
            elem["value"] for elem in poi["Attribute"] if elem["name"] == "StoreType"
        ]
        location_type = location_type[0] if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = [
            elem["value"]
            for elem in poi["Attribute"]
            if elem["name"] == "Hours of Operation"
        ]
        hours_of_operation = hours_of_operation[0].replace("<br>", " ")
        hours_of_operation = (
            hours_of_operation if hours_of_operation.strip() else "<MISSING>"
        )
        if hours_of_operation == "N/A":
            hours_of_operation = "<MISSING>"

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
