import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "europcar.co.uk"
    start_url = "https://applications.europcar.com/stationfinder/stationfinder?query=getAllCountriesStations&callback=jQuery16104922423739873101_1652176658603&lg=en_US"

    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text.split("_1652176658603(")[-1][:-2])
    for country_code, all_locations in data["allCoutriesStations"].items():
        for poi in all_locations:
            store_number = poi["code"]
            page_url = f"https://www.europcar.com/DotcarClient/step1.action?checkinStation={store_number}&checkoutStation={store_number}&checkoutCountry={country_code}&selectedtab=undefined"

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["details"]["stationName"],
                street_address=poi["details"]["street"],
                city=poi["details"]["city"],
                state="",
                zip_postal=poi["details"].get("postcode"),
                country_code=country_code,
                store_number="",
                phone=poi["details"].get("phone"),
                location_type="",
                latitude=poi["details"]["latitude"],
                longitude=poi["details"]["longitude"],
                hours_of_operation="",
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
