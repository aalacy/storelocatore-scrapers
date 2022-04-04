import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    domain = "orangejulius.com"
    session = SgRequests()
    start_url = "https://prod-orangejulius-dairyqueen.dotcmscloud.com/api/vtl/locations?country=us&lat={}&long={}"

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=200
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng))
        data = json.loads(response.text)
        all_locations = data["locations"]

        for poi in all_locations:
            page_url = "https://www.dairyqueen.com/en-us" + poi["url"]
            location_name = poi["title"]
            location_name = (
                location_name.split(":")[-1].strip() if location_name else ""
            )
            street_address = poi["address3"]
            city = poi["city"]
            state = poi["stateProvince"]
            zip_code = poi["postalCode"]
            country_code = poi["country"]
            store_number = poi["storeNo"]
            location_type = poi["conceptType"]
            if poi["tempClosed"] or poi["comingSoon"]:
                continue
            latitude = poi["latlong"].split(",")[0]
            longitude = poi["latlong"].split(",")[1]
            hoo = poi.get("storeHours")
            days = {
                "1": "Monday",
                "2": "Tuesday",
                "3": "Wednesday",
                "4": "Thursday",
                "5": "Friday",
                "6": "Saturday",
                "7": "Sunday",
            }
            hoo_clean = []
            if hoo:
                hoo = hoo.split(",")
                for i, day in days.items():
                    for e in hoo:
                        if i == e[0]:
                            e = day + e[1:]
                            hoo_clean.append(e)
            hoo = ", ".join(hoo_clean)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone="",
                location_type=location_type,
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
