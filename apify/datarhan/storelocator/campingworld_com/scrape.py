import csv
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "campingworld.com"
    start_url = "https://rv.campingworld.com/dealersinradius?miles=400&lat={}&lon={}&locationsearch=true"

    all_locations = []
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=250
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng))
        all_codes = response.text[1:-1]

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "cookie": f"liveagent_oref=https://www.campingworld.com/; liveagent_vc=4; cw_searchLat={lat}; cw_searchLon={lng}; cw_searchDealers={all_codes}",
        }

        url = "https://rv.campingworld.com/api/locationcards"
        params = {
            "limit": "1000",
            "glcodes": all_codes,
            "lat": lat,
            "lon": lng,
            "locationsearch": "true",
            "service": "true",
        }
        data = session.get(url, params=params, headers=headers).json()
        all_locations += data["locations"]

    for poi in all_locations:
        base_url = "https://rv.ganderoutdoors.com/dealer/"
        store_url = urljoin(base_url, poi["dealer_url"])
        location_name = poi["marketingname"]
        location_name = location_name if location_name else "<MISSING>"
        if "camping world" not in location_name.lower():
            continue
        street_address = poi["billing_street"]
        city = poi["billing_city"]
        state = poi["statecode"]
        zip_code = poi["billing_zip"]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phonenumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lon"]
        mf_open = poi["store_hours_mf_open"]
        mf_close = poi["store_hours_mf_closed"]
        sat_open = poi["store_hours_sat_open"]
        sat_close = poi["store_hours_sat_closed"]
        sun_open = poi["store_hours_sun_open"]
        sun_close = poi["store_hours_sun_closed"]
        hours_of_operation = f"Mon-Fri: {mf_open} - {mf_close} Sat: {sat_open} - {sat_close} Sun: {sun_open} - {sun_close}"

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        if store_url not in scraped_items:
            scraped_items.append(store_url)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
