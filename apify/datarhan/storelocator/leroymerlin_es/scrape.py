# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.leroymerlin.es/tiendas.geoglobal.json"
    domain = "leroymerlin.es"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for poi in data["features"]:
        hoo = []
        for day, hours in poi["properties"]["schedule"].items():
            hoo.append(f'{day}: {hours[0]["from"]} - {hours[0]["to"]}')
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.leroymerlin.es" + poi["properties"]["path"],
            location_name=poi["properties"]["name"],
            street_address=poi["properties"]["street"],
            city=poi["properties"]["city"],
            state=poi["properties"].get("region"),
            zip_postal=poi["properties"]["zip"],
            country_code="ES",
            store_number=poi["properties"]["code"],
            phone=poi["properties"]["phone"],
            location_type="",
            latitude=poi["properties"]["materialsProperties"]["gpsCoordinates"].get(
                "latitude"
            ),
            longitude=poi["properties"]["materialsProperties"]["gpsCoordinates"].get(
                "longitude"
            ),
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
