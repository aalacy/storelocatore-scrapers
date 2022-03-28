from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.aldi-sued.de/de/de/.get-stores-in-radius.json?_1630664498068=&latitude=52.33187999999999&longitude=10.4411716&radius=25000"
    domain = "aldi-sued.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    for poi in data["stores"]:
        if not poi.get("streetAddress"):
            continue
        if poi["storeType"] == "S":
            location_name = "ALDI SÜD"
        else:
            location_name = "ALDI NORD"
        hoo = []
        for e in poi["openUntilSorted"]["openingHours"]:
            day = e["day"]
            if e.get("closed"):
                hoo.append(f"{day}: closed")
            else:
                closes = e["closeFormatted"]
                opens = e["openFormatted"]
                hoo.append(f"{day}: {opens} - {closes}")
        hoo = ", ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.aldi-sued.de/de/filialen.html",
            location_name=location_name,
            street_address=poi["streetAddress"],
            city=poi["city"],
            state="",
            zip_postal=poi["postalCode"],
            country_code=poi["countryCode"],
            store_number=poi["storeId"],
            phone="",
            location_type="",
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
