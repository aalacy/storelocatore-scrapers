import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    start_url = "https://cdn.storelocatorwidgets.com/json/eec4d05bca098b89dc086655f7f5e047?callback=slw"
    domain = "cinnabon.uk"
    data = session.get(start_url)
    data = json.loads(data.text.replace("slw(", "")[:-1])
    for poi in data["stores"]:
        if poi["filters"] != ["Cinnabon"]:
            continue
        hoo = ""
        raw_data = (
            poi["data"]["address"].replace("\r\n", ", ").replace(",,", ",").split(", ")
        )
        raw_address = ", ".join(raw_data)
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        city = addr.city
        zip_code = addr.postcode
        if not zip_code:
            zip_code = raw_address.split(",")[-1].strip()
            if zip_code:
                if len(zip_code.split()[-1]) > 3:
                    zip_code = ""

        if poi["data"].get("hours_Monday"):
            mon = f'Monday: {poi["data"]["hours_Monday"]}'
            tue = f'Tuesday: {poi["data"]["hours_Tuesday"]}'
            wed = f'Wednesday: {poi["data"]["hours_Wednesday"]}'
            thu = f'Thursday: {poi["data"]["hours_Thursday"]}'
            fri = f'Friday" {poi["data"]["hours_Friday"]}'
            sat = f'Saturday: {poi.get("data", {}).get("hours_Saturday")}'
            sun = f'Sunday: {poi["data"]["hours_Sunday"]}'
            hoo = f"{mon}, {tue}, {wed}, {thu}, {fri}, {sat}, {sun}"

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.cinnabon.uk/stores",
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state="",
            zip_postal=zip_code,
            country_code="",
            store_number=poi["storeid"],
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
