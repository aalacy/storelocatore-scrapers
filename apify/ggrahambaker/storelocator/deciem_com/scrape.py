import re
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():

    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    scraped_items = []

    start_url = "https://deciem.com/on/demandware.store/Sites-deciem-global-Site/en_ES/Stores-FindStores?lat={}&long={}&radius=100&distanceUnit=mi"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_coords = DynamicGeoSearch(
        country_codes=[
            SearchableCountries.USA,
            SearchableCountries.BRITAIN,
            SearchableCountries.CANADA,
        ],
        max_search_distance_miles=100,
    )
    for lat, lng in all_coords:
        all_locations = []
        try:
            response = session.get(start_url.format(lat, lng), headers=hdr)
            all_locations = json.loads(response.text)["stores"]
        except:
            try:
                session = SgRequests()
                response = session.get(start_url.format(lat, lng), headers=hdr)
                all_locations = json.loads(response.text)["stores"]
            except:
                continue
        for poi in all_locations:
            store_url = "https://deciem.com/es/find-us"

            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address1"]
            if poi["address2"]:
                street_address += " " + poi["address2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi.get("stateCode")
            state = state if state else "<MISSING>"
            zip_code = poi["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["countryCode"]
            country_code = country_code if country_code else "<MISSING>"
            if country_code not in ["CA", "GB", "US"]:
                continue
            store_number = "<MISSING>"
            try:
                phone = poi["phone"].strip()
            except:

                phone = "<MISSING>"
            location_type = poi["owner"]
            latitude = poi["latitude"]
            longitude = poi["longitude"]
            try:
                hours_of_operation = poi["storeHours"].replace("\n", " ").strip()
            except:
                hours_of_operation = "<MISSING>"
            check = f"{location_name} {street_address}"
            if check not in scraped_items:
                scraped_items.append(check)
                yield SgRecord(
                    locator_domain=domain,
                    page_url=store_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
