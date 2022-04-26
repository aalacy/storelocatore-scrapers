import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://interceramicusa.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=25&search_radius=100&autoload=1"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=100
    )
    for lat, lng in all_coords:
        all_locations = session.get(start_url.format(lat, lng), headers=hdr).json()
        for poi in all_locations:
            store_url = "https://interceramicusa.com/dealer-locator/"
            location_name = poi["store"]
            location_name = location_name if location_name else "<MISSING>"
            location_name = location_name.replace("&#038;", "&").replace("&#8217;", "'")
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["state"]
            state = state.split("-")[0] if state else "<MISSING>"
            street_address = poi["address"]
            if f"{state}.".lower() in street_address.lower():
                street_address = street_address.split(", ")[0]
            if city.lower() in street_address.lower():
                street_address = street_address.split(", ")[0]
            if city.lower() in street_address.lower():
                street_address = street_address.split(city)[0].strip()
            street_address = (
                street_address.split(", La ")[0] if street_address else "<MISSING>"
            )
            zip_code = poi["zip"]
            zip_code = zip_code.split()[-1] if zip_code else "<MISSING>"
            country_code = poi["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["display_type"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSINg>"
            longitude = poi["lng"]
            longitude = longitude if longitude else "<MISSING>"
            hoo = etree.HTML(poi["hours"])
            hoo = hoo.xpath("//text()")
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
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
