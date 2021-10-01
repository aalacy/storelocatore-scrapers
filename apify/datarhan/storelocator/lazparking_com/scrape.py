from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()

    start_url = "https://xpark.lazparking.com/api/v1/Locations/FindLocationsByLatLng?nelat=40.73567202773479&nelng=-73.89595663283615&swlat=40.68987069570836&swlng=-74.11598896716384&type=&mode=&layout=&_"
    domain = "lazparking.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=10
    )
    for lat, lng in all_coords:
        all_locations = session.get(
            start_url.format(lat, lng, lat - 0.05, lng - 0.13), headers=hdr
        ).json()
        for poi in all_locations:
            street_address = poi["Address1"]
            if poi["Address2"]:
                street_address += " " + poi["Address2"]
            hoo = ""
            if "Open 24/7" in poi["Amenities"]:
                hoo = "Open 24/7"

            item = SgRecord(
                locator_domain=domain,
                page_url=start_url,
                location_name=poi["Name"],
                street_address=street_address,
                city=poi["City"].split(",")[0],
                state=poi["State"],
                zip_postal=poi["Zip"],
                country_code="",
                store_number=poi["LocNo"],
                phone=poi["Phone"],
                location_type=poi["OperationMode"],
                latitude=poi["Latitude"],
                longitude=poi["Longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
