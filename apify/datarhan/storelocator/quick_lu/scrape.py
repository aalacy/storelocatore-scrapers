# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.quick.lu/fr/Ajax/loadRestaurantsData"
    domain = "quick.lu"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()
    for store_number, poi in data["restaurants"].items():
        hoo = []
        days = {
            "1": "Lundi",
            "2": "Mardi",
            "3": "Mercredi",
            "4": "Jeudi",
            "5": "Vendredi",
            "6": "Samedi",
            "7": "Dimanche",
        }
        for i, hours in poi["opening_hours_processed"].items():
            if hours["opening"]:
                opens = hours["opening"][0]["from_hour"]
                closes = hours["opening"][0]["to_hour"]
                hoo.append(f"{days[i]}: {opens}-{closes}")
            else:
                hoo.append(f"{days[i]}: closed")
        hoo = " ".join(hoo)

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.quick.lu/fr/restaurant/" + poi["slug_nl"],
            location_name=poi["title"],
            street_address=poi["address"],
            city=poi["locality"],
            state="",
            zip_postal=poi["postal_code"],
            country_code=poi["country"],
            store_number=store_number,
            phone=poi["telephone"],
            location_type="",
            latitude=poi["location_lat"],
            longitude=poi["location_lng"],
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
