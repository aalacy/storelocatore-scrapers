import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "olympiasports.net"
    start_url = "https://cdn.storelocatorwidgets.com/json/MCTYcb63A5zRmDDdPtrI6AtjcG7tnjbW?callback=slw&_=1651226854861"
    response = session.get(start_url)
    data = json.loads(response.text.replace("slw(", "")[:-1])

    for poi in data["stores"]:
        raw_address = poi["data"]["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        mon = f"Monday: {poi['data']['hours_Monday']}"
        tue = f"Tuesday: {poi['data']['hours_Tuesday']}"
        wed = f"Wednesday: {poi['data']['hours_Tuesday']}"
        thu = f"Thursday: {poi['data']['hours_Thursday']}"
        fri = f"Friday: {poi['data']['hours_Friday']}"
        sat = f"Saturday: {poi['data']['hours_Saturday']}"
        sun = f"Sunday: {poi['data']['hours_Sunday']}"
        hoo = f"{mon}, {tue}, {wed}, {thu}, {fri}, {sat}, {sun}"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://olympiasports.net/store-locator",
            location_name=poi["name"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=poi["name"].split("-")[-1],
            phone=poi["data"].get("phone"),
            location_type="",
            latitude=poi["data"]["map_lat"],
            longitude=poi["data"]["map_lng"],
            hours_of_operation=hoo,
            raw_address=raw_address,
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
