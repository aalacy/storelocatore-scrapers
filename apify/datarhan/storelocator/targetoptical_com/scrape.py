from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://www.targetoptical.com/wcs/resources/store/12001/storelocator/filtered/latitude/{}/longitude/{}?pageSize=100&offset=0"
    domain = "targetoptical.com"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
    }
    frm = {
        "selectedInsuranceFilters": [],
        "selectedLanguageFilters": [],
        "selectedOpeningFilters": [],
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        data = session.post(start_url.format(lat, lng), json=frm, headers=hdr)
        if data.status_code != 200:
            continue
        data = data.json()
        if not data.get("PhysicalStore"):
            continue
        all_locations = data["PhysicalStore"]
        for poi in all_locations:
            location_name = poi["Description"][0]["displayStoreName"]
            hours = [e for e in poi["Attribute"] if e["name"] == "StoreHours"][0][
                "displayValue"
            ].split("; ")
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            hoo = list(map(lambda d, h: d + " " + h, days, hours))
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.targetoptical.com/to-us/locations",
                location_name=location_name,
                street_address=" ".join(poi["addressLine"]),
                city=poi["city"],
                state=poi["stateOrProvinceName"],
                zip_postal=poi["postalCode"],
                country_code=poi["country"],
                store_number=poi["storeName"],
                phone=poi["telephone1"],
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
