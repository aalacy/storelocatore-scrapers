import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests()
    start_url = "https://www.goretailgroup.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=200"
    domain = "goretailgroup.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=10
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng), headers=hdr)
        if response.text and response.text.strip():
            all_locations = json.loads(response.text)
            for poi in all_locations:
                store_url = poi["url"]
                store_url = (
                    store_url
                    if store_url
                    else "https://www.goretailgroup.com/locations-facilities/"
                )
                location_name = poi["store"]
                location_name = location_name if location_name else "<MISSING>"
                street_address = poi["address"]
                if poi["address2"]:
                    street_address += " " + poi["address2"]
                street_address = (
                    street_address.split(" Go!")[0] if street_address else "<MISSING>"
                )
                city = poi["city"]
                city = city if city else "<MISSING>"
                state = poi["state"]
                state = state if state else "<MISSING>"
                zip_code = poi["zip"]
                zip_code = zip_code if zip_code else "<MISSING>"
                country_code = poi["country"]
                country_code = country_code if country_code else "<MISSING>"
                store_number = poi["id"]
                phone = poi["phone"]
                phone = phone if phone else "<MISSING>"
                location_type = "<MISSING>"
                latitude = poi["lat"]
                longitude = poi["lng"]
                hoo = etree.HTML(poi["hours"]).xpath("//text()")
                hoo = [e.strip() for e in hoo if e.strip()]
                hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

                item = SgRecord(
                    locator_domain=domain,
                    page_url=store_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
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
