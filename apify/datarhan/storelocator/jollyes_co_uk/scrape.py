import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "jollyes.co.uk"
    start_url = "https://api.jollyes.co.uk/api/ext/aureatelabs/storeList"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["result"]:
        page_url = "https://www.jollyes.co.uk/store/{}".format(poi["uid"])
        hoo = []
        for key, value in poi.items():
            if "Opening" in key:
                day = key.replace("Opening", "")
                if value:
                    opens = value[:2] + ":" + value[2:]
                    closes = poi["{}Closing".format(day)]
                    closes = closes[:2] + ":" + closes[2:]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")
        hoo = " ".join(hoo) if hoo else ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=poi["streetAddress"],
            city=poi["city"],
            state=poi["county"],
            zip_postal=poi["postCode"],
            country_code="",
            store_number="",
            phone=poi["phoneNumber"],
            location_type="",
            latitude=poi["map"]["latitude"],
            longitude=poi["map"]["longitude"],
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
