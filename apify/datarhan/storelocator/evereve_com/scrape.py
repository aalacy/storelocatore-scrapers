import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "evereve.com"
    start_url = "https://evereve.com/amlocator/index/ajax/"
    formdata = {
        "lat": "",
        "lng": "",
        "radius": "",
        "mapId": "amlocator-map-canvas5fef59650b3e7",
        "storeListId": "amlocator_store_list5fef596505523",
        "product": "0",
        "category": "0",
        "sortByDistance": "1",
        "p": "ajax",
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["items"]:
        store_url = "https://evereve.com/stores/" + poi["url_key"]
        location_name = poi["name"]
        if "Coming Soon" in location_name:
            continue
        street_address = poi["address"]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["url_key"].split("/")[0]
        state = state.upper() if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if poi["schedule_array"]:
            for day, hours in poi["schedule_array"].items():
                opens = "{}:{}".format(hours["from"]["hours"], hours["from"]["minutes"])
                closes = "{}:{}".format(hours["to"]["hours"], hours["to"]["minutes"])
                hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            " ".join(hours_of_operation).replace("00:00 - 00:00", "closed")
            if hours_of_operation
            else "<MISSING>"
        )

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
