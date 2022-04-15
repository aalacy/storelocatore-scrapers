import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    domain = "alonbrands.com"
    start_url = "https://alonbrands.com/wp-admin/admin-ajax.php"
    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        formdata = {
            "action": "get_stores",
            "lat": lat,
            "lng": lng,
            "radius": "100",
        }

        response = session.post(start_url, headers=hdr, data=formdata)
        data = json.loads(response.text)

        for n, poi in data.items():
            item = SgRecord(
                locator_domain=domain,
                page_url=poi["gu"],
                location_name=poi["na"],
                street_address=poi["st"],
                city=poi["ct"],
                state=poi["rg"],
                zip_postal=poi["zp"],
                country_code="",
                store_number=poi["ID"],
                phone=poi.get("te"),
                location_type="",
                latitude=poi["lat"],
                longitude=poi["lng"],
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
