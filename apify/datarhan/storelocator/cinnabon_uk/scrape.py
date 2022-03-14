import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://cdn.storelocatorwidgets.com/json/eec4d05bca098b89dc086655f7f5e047?callback=slw"
    domain = "cinnabon.uk"
    data = session.get(start_url)
    data = json.loads(data.text.replace("slw(", "")[:-1])
    for poi in data["stores"]:
        hoo = ""
        raw_data = poi["data"]["address"].replace("\r\n", ", ").split(", ")
        if len(raw_data) == 2:
            raw_data.insert(1, "")
        if len(raw_data) == 1:
            raw_data.insert(0, "")
            raw_data.insert(1, "")

        if poi["data"].get("hours_Monday"):
            mon = f'Monday: {poi["data"]["hours_Monday"]}'
            tue = f'Tuesday: {poi["data"]["hours_Tuesday"]}'
            wed = f'Wednesday: {poi["data"]["hours_Wednesday"]}'
            thu = f'Thursday: {poi["data"]["hours_Thursday"]}'
            fri = f'Friday" {poi["data"]["hours_Friday"]}'
            sat = f'Saturday: {poi["data"]["hours_Saturday"]}'
            sun = f'Sunday: {poi["data"]["hours_Sunday"]}'
            hoo = f"{mon}, {tue}, {wed}, {thu}, {fri}, {sat}, {sun}"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.cinnabon.uk/stores",
            location_name=poi["name"],
            street_address=raw_data[0],
            city=raw_data[1],
            state="",
            zip_postal=raw_data[2],
            country_code="",
            store_number=poi["storeid"],
            phone=poi["data"].get("phone"),
            location_type="",
            latitude=poi["data"]["map_lat"],
            longitude=poi["data"]["map_lng"],
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
