from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://uberall.com/api/storefinders/ALDINORDNL_8oqeY3lnn9MTZdVzFn4o0WCDVTauoZ/locations/all?v=20211005&language=nl&fieldMask=id&fieldMask=identifier&fieldMask=googlePlaceId&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&fieldMask=openingHours&fieldMask=phone"
    domain = "aldi.nl"

    data = session.get(start_url).json()
    for poi in data["response"]["locations"]:
        city = poi["city"]
        street_address = poi["streetAndNumber"]
        store_number = poi["id"]
        page_url = f"https://www.aldi.nl/supermarkt.html/l/{city.lower().replace(' ', '-')}/{street_address.lower().replace(' ', '-')}/{store_number}"
        hoo = []
        days = {
            7: "Sunday",
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
        }
        for e in poi["openingHours"]:
            day = days[e["dayOfWeek"]]
            if e.get("closed"):
                hoo.append(f"{day}: closed")
            else:
                opens = e["from1"]
                closes = e["to1"]
            hoo.append(f"{day}: {opens} - {closes}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=poi["province"],
            zip_postal=poi["zip"],
            country_code=poi["country"],
            store_number=store_number,
            phone=poi["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
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
