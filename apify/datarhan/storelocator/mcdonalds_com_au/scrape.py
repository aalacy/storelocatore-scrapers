from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://mcdonalds.com.au/data/store"
    domain = "mcdonalds.com.au"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        hoo = []
        for e in poi["store_trading_hour"][1:]:
            if e[1] == e[2] == "0000":
                hoo.append(f"{e[0]} 24h")
            else:
                opens = e[-1][:2] + ":" + e[-1][2:]
                closes = e[-1][:2] + ":" + e[-1][2:]
                hoo.append(f"{e[0]} {opens} - {closes}")
        hours_of_operation = " ".join(hoo).replace("99:99 - 99:99", "closed")
        latitude = ""
        longitude = ""
        if poi["lat_long"]:
            latitude = poi["lat_long"]["lat"]
            longitude = poi["lat_long"]["lon"]

        item = SgRecord(
            locator_domain=domain,
            page_url="https://mcdonalds.com.au/find-us/restaurants",
            location_name=poi["title"],
            street_address=poi["store_address"],
            city=poi["store_suburb"],
            state=poi["store_state"],
            zip_postal=poi["store_postcode"],
            country_code="AU",
            store_number=poi["store_code"],
            phone=poi["store_phone"],
            location_type=SgRecord.MISSING,
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
