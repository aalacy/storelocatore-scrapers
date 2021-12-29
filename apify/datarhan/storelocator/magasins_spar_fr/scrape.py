from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = (
        "https://magasins.spar.fr/api/v3/locations?size=100&near={},{}&language=fr"
    )
    domain = "magasins.spar.fr"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.FRANCE], expected_search_radius_miles=25
    )
    for lat, lng in all_coords:
        all_locations = session.get(start_url.format(lat, lng), headers=hdr).json()
        for poi in all_locations:
            hoo = []
            days = {
                1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Satarday",
                7: "Sunday",
            }
            for e in poi["businessHours"]:
                day = days[e["startDay"]]
                opens = e["openTimeFormat"]
                closes = e["closeTimeFormat"]
                hoo.append(f"{day} {opens} - {closes}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["contact"]["url"],
                location_name=poi["name"],
                street_address=poi["address"]["street"],
                city=poi["address"]["locality"],
                state="",
                zip_postal=poi["address"]["zipCode"],
                country_code=poi["address"]["country"],
                store_number="",
                phone=poi["contact"]["phone"],
                location_type="",
                latitude=poi["address"]["latitude"],
                longitude=poi["address"]["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
