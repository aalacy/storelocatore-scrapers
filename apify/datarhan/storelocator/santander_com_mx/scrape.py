# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "santander.com.mx"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.URUGUAY,
            SearchableCountries.MEXICO,
            SearchableCountries.SPAIN,
            SearchableCountries.ARGENTINA,
            SearchableCountries.PORTUGAL,
            SearchableCountries.GERMANY,
            SearchableCountries.POLAND,
            SearchableCountries.BRAZIL,
            SearchableCountries.CHILE,
            SearchableCountries.USA,
            SearchableCountries.PUERTO_RICO
        ],
        expected_search_radius_miles=100,
    )
    for lat, lng in all_coords:
        start_url = f"https://back-scus.azurewebsites.net/branch-locator/find/defaultView?config=%7B%22coords%22%3A%5B{lat}%2C{lng}%5D%7D&globalSearch=true"
        all_locations = session.get(start_url.format(lat, lng), headers=hdr).json()
        for poi in all_locations:
            hoo = []
            for day, hours in poi["schedule"]["workingDay"].items():
                if hours:
                    hoo.append(f"{day}: {hours[0]}")
                else:
                    hoo.append(f"{day}: closed")
            hoo = " ".join(hoo)
            street_address = poi["location"]["address"]
            if street_address:
                street_address = street_address.split(", C.P")[0]
            zip_code = poi["location"]["zipcode"]
            if zip_code and street_address:
                street_address = street_address.split(zip_code)[0]

            item = SgRecord(
                locator_domain=domain,
                page_url=poi["urlDetailPage"],
                location_name=poi.get("name"),
                street_address=street_address,
                city=poi["location"]["city"],
                state="",
                zip_postal=zip_code,
                country_code=poi["location"]["country"],
                store_number=poi["poicode"],
                phone=poi.get("contactData", {}).get("phoneNumber"),
                location_type="",
                latitude=poi["location"]["coordinates"][1],
                longitude=poi["location"]["coordinates"][0],
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
