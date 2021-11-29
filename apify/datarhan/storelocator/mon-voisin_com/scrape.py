import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "mon-voisin.com"
    start_url = "https://www.mon-voisin.com/wp-admin/admin-ajax.php"

    all_locations = []
    page = "1"
    formdata = {
        "action": "search_nearest_stores",
        "lng": "-73.9917114",
        "lat": "45.5597832",
        "page": page,
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    data = session.post(start_url, data=formdata, headers=headers).json()
    all_locations = data["stores"]
    total_pages = data["total_page"]
    for page in range(2, total_pages + 1):
        formdata["page"] = str(page)
        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)
        for poi in data["stores"].values():
            all_locations.append(poi)

    for poi in all_locations:
        if type(poi) == str:
            continue
        store_url = "https://www.mon-voisin.com" + poi["url"]
        location_name = poi["store"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["store"]["address_1"]
        if poi["store"]["address_2"]:
            street_address += ", " + poi["store"]["address_2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["store"]["city"]
        city = city if city else "<MISSING>"
        state = poi["store"]["province"]
        state = state if state else "<MISSING>"
        zip_code = poi["store"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["store"]["store_number"]
        phone = poi["store"]["phone"]
        phone = phone if phone else "<MISSING>"
        latitude = poi["store"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["store"]["lng"]
        longitude = longitude if longitude else "<MISSING>"
        location_type = ", ".join(poi["store"]["services"])
        location_type = location_type if location_type else "<MISSING>"
        hours_of_operation = []
        for elem in poi["store"]["hours"]:
            day = elem["day"]
            hours = elem["hours"]
            hours_of_operation.append(f"{day} {hours}")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
