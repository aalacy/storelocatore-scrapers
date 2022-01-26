from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    start_url = "https://www.hofer.at/at/de/.get-stores-in-radius.json?_1630317579779&latitude=48.0819112&longitude=13.8589415&radius=50000"
    domain = "hofer.at"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr).json()

    all_locations = response["stores"]
    for poi in all_locations:
        hoo = []
        for e in poi["openUntilSorted"]["openingHours"]:
            day = e["day"]
            if e.get("closed"):
                hoo.append(f"{day}: closed")
            else:
                opens = e["openFormatted"]
                closes = e["closeFormatted"]
                hoo.append(f"{day}: {opens} - {closes}")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.hofer.at/de/filialen.html",
            location_name=poi["displayName"],
            street_address=poi["streetAddress"],
            city=poi["city"].split(".,")[-1].split(",")[-1].strip(),
            state=SgRecord.MISSING,
            zip_postal=poi["postalCode"],
            country_code=poi["countryCode"],
            store_number=poi["storeId"],
            phone=poi.get("phoneNumber"),
            location_type=poi["storeType"],
            latitude=poi["latitude"],
            longitude=poi["longitude"],
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
