# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.mueller.{}/api/ccstore/allPickupStores/"
    domain = "mueller.de"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_countries = ["de", "at", "ch", "hr", "co.hu", "si", "es"]
    for country_code in all_countries:
        all_locations = session.get(start_url.format(country_code), headers=hdr).json()
        for poi in all_locations:
            location_type = poi["sections"]
            if location_type.startswith(","):
                location_type = location_type[1:]
            poi_data = session.get(
                f'https://www.mueller.{country_code}/api/ccstore/byStoreNumber/{poi["storeNumber"]}/'
            ).json()
            hoo = []
            if poi_data.get("cCStoreDtoDetails"):
                for e in poi_data["cCStoreDtoDetails"]["openingHourWeek"]:
                    if e["open"]:
                        hoo.append(f'{e["dayOfWeek"]}: {e["fromTime"]} - {e["toTime"]}')
                    else:
                        hoo.append(f'{e["dayOfWeek"]}: closed')
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.mueller.de/meine-filiale/",
                location_name=poi["storeName"],
                street_address=poi["street"],
                city=poi["city"],
                state="",
                zip_postal=poi["zip"],
                country_code=poi["country"],
                store_number=poi["storeNumber"],
                phone=poi_data["cCStoreDtoDetails"]["phone"],
                location_type=location_type,
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
