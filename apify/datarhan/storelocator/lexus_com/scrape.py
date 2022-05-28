import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "lexus.com"
    start_url = "https://www.lexus.com/rest/lexus/dealers?experience=dealers"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data["dealers"]:
        page_url = "https://www.lexus.com/dealers/{}-{}".format(
            poi["id"], poi["dealerName"].lower().replace(" ", "-")
        )
        location_name = poi["dealerName"]
        street_address = poi["dealerAddress"]["address1"]
        city = poi["dealerAddress"]["city"]
        state = poi["dealerAddress"]["state"]
        zip_code = poi["dealerAddress"]["zipCode"]
        store_number = poi["id"]
        phone = poi["dealerPhone"]
        latitude = poi["dealerLatitude"]
        longitude = poi["dealerLongitude"]
        hours_of_operation = []
        if poi.get("hoursOfOperation"):
            if poi["hoursOfOperation"].get("Sales"):
                for day, hours in poi["hoursOfOperation"]["Sales"].items():
                    hours_of_operation.append(f"{day} {hours}")
            elif poi["hoursOfOperation"].get("General"):
                for day, hours in poi["hoursOfOperation"]["General"].items():
                    hours_of_operation.append(f"{day} {hours}")
            else:
                for day, hours in poi["hoursOfOperation"]["Service"].items():
                    hours_of_operation.append(f"{day} {hours}")
        hours_of_operation = " ".join(hours_of_operation) if hours_of_operation else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code="",
            store_number=store_number,
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
