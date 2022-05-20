import csv
import json

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests


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
    session = SgRequests().requests_retry_session(retries=1, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "dollar.bank"
    start_url = "https://locations.dollar.bank/api/locations/dollar"

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=50,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        body = '{"radius":50,"center":{"latitude":%s,"longitude":%s},"branchTypeFilters":[{"image":null,"title":"Branches","value":"office","isChecked":true},{"image":null,"title":"Drive-Thru","value":"drivethru_hours","isChecked":true},{"image":null,"title":"Loan Centers","value":"loan_center_hours","isChecked":true}],"branchFeatures":[{"image":null,"title":"Private Banking","value":"private_banking_office","isChecked":true}],"atmFilter":[{"image":"https://assets-us-01.kc-usercontent.com/d7f410bf-ce32-001c-8d9a-4f99a8804c0d/3bbf253d-da17-4295-96cc-b4c0a236598c/DB-icon.png?width=35&height=35","title":"Dollar Bank ATM","value":"has_atm","isChecked":true},{"image":"https://assets-us-01.kc-usercontent.com/d7f410bf-ce32-001c-8d9a-4f99a8804c0d/2f0f570a-868b-48b6-a453-dde7a81b9279/freedom-atm-icon.png?width=35&height=35","title":"Freedom ATM","value":"freedom_atm","isChecked":false},{"image":"https://assets-us-01.kc-usercontent.com/d7f410bf-ce32-001c-8d9a-4f99a8804c0d/88dec82d-e724-419d-a662-218ce911ada3/allpoint-icon.png?width=35&height=35","title":"Allpoint ATM","value":"Allpoint","isChecked":false}]}'
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
            "Content-Type": "application/json",
            "Host": "locations.dollar.bank",
            "Cookie": "BIGipServerlocations_dollar_bank_https.app~locations_dollar_bank_https_pool=3624344074.47873.0000; _gcl_au=1.1.1897968214.1610053191; nmstat=1c8287f1-0d5f-b862-d498-fdfefee8feed; _fbp=fb.1.1610053192394.73768629; _gid=GA1.2.1262018703.1610299821; _ga_Y4EF12QV9V=GS1.1.1610299820.8.0.1610299820.0; _ga=GA1.1.1225520427.1610053191; _dc_gtm_UA-18144621-12=1; _gali=autocomplete",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        }
        response = session.post(
            "https://locations.dollar.bank/api/locations/dollar",
            data=body % (lat, lng),
            headers=headers,
        )
        response = session.post(start_url, data=body % (lat, lng), headers=headers)
        data = json.loads(response.text)
        all_locations += data

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = poi["name"]
        raw_address = poi["address"].split(", ")
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[2].split()[0]
        zip_code = raw_address[2].split()[-1]
        country_code = raw_address[-1]
        store_number = poi["id"]
        phone = "<MISSING>"
        location_type = poi["locationType"]
        latitude = poi["position"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["position"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

        if len(zip_code) == 2:
            zip_code = "<MISSING>"

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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
