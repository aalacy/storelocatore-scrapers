import csv
import json
from sgzip.static import static_zipcode_list, SearchableCountries
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed


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
            for line in row:
                writer.writerow(line)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "bbt.com"
    start_url = "https://www.bbt.com/clocator/searchLocations.do?quickZip={}&type=branch&services="

    all_codes = static_zipcode_list(
        country_code=SearchableCountries.USA,
        radius=10,
    )

    hdr = {
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Host": "www.bbt.com",
        "Referer": "https://www.bbt.com/locator/search.html",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    items = scrape_loc_urls(
        all_codes, hdr, start_url, DOMAIN, scraped_items, items, session
    )

    return items


def parallel_run(code, hdr, start_url, DOMAIN, scraped_items, items, session):
    passed = False
    while not passed:
        response = session.get(start_url.format(code), headers=hdr)
        if "Access Denied" not in response.text:
            passed = True

    if response.text.endswith("}}"):
        data = json.loads(response.text)
    elif response.text.endswith('"'):
        data = json.loads(response.text + "}}")
    else:
        data = json.loads(response.text + '"}}')

    for poi in data["locationsFound"]:
        store_url = "<MISSING>"
        location_name = poi["locationName"]

        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += " " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["centerATMNumber"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["locationType"]
        if location_type == "Branch":
            location_type = "Branch/ATM"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["lobbyHours"]
        hours_of_operation = (
            ", ".join(hours_of_operation).replace("  ", " ")
            if hours_of_operation
            else "<MISSING>"
        )

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

        if poi["locationKey"] not in scraped_items:
            scraped_items.append(poi["locationKey"])
            yield item


def scrape_loc_urls(all_codes, hdr, start_url, DOMAIN, scraped_items, items, session):
    items = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                parallel_run,
                code,
                hdr,
                start_url,
                DOMAIN,
                scraped_items,
                items,
                session,
            )
            for code in all_codes
        ]
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    items.append(record)
            except Exception:
                pass

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
