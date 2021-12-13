from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.toyota.com.sa/api/feature/findcenter/getcenters?parentID=481b6c75-740b-42d0-bd05-b84008e9bcbe&formattedAddress=&boundsNorthEast=&boundsSouthWest="
    domain = "toyota.com.sa"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        hoo = []
        for e in poi["toyotaCenterTiming"]:
            day = e["DayTitle"]
            if e["DayOpeningTiming"]:
                opens = e["DayOpeningTiming"]
                closes = e["DayClosingTiming"]
                hoo.append(f"{day} {opens} - {closes}")
            else:
                hoo.append(f"{day} Closed")
        hoo = " ".join(hoo)
        location_type = poi["category"].strip()
        if location_type.endswith(","):
            location_type = location_type[:-1]
        if "Showrooms" not in location_type:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.toyota.com.sa/en/find-a-center",
            location_name=poi["name"],
            street_address=street_address,
            city=poi["city"],
            state=poi["state"],
            zip_postal=poi["postal"],
            country_code="SA",
            store_number="",
            phone=poi["phone"].split("/")[0].strip(),
            location_type=location_type,
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
