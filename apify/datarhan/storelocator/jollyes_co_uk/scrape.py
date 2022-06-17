from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "jollyes.co.uk"

    data = session.get("https://www.jollyes.co.uk/api/ext/story-blok/get-stores").json()
    for poi in data["result"]["StoreItems"]["items"]:
        page_url = f"https://www.jollyes.co.uk/store/{poi['slug']}"
        hoo = []
        for key, value in poi["content"]["storeTime"][0].items():
            if "Opening" in key:
                day = key.replace("Opening", "")
                if value:
                    opens = value[:2] + ":" + value[2:]
                    closes = poi["content"]["storeTime"][0]["{}Closing".format(day)]
                    closes = closes[:2] + ":" + closes[2:]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")
        hoo = " ".join(hoo) if hoo else ""
        latitude = poi["content"]["location"][0]["latitude"]
        longitude = poi["content"]["location"][0]["longitude"]
        if latitude == "100":
            latitude = ""
            longitude = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["content"]["name"],
            street_address=poi["content"]["location"][0]["streetAddress"],
            city=poi["content"]["location"][0]["city"],
            state=poi["content"]["location"][0]["county"],
            zip_postal=poi["content"]["location"][0]["postCode"],
            country_code="",
            store_number=poi["content"]["warehouseId"],
            phone=poi["content"]["phoneNumber"],
            location_type="",
            latitude=latitude,
            longitude=longitude,
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
