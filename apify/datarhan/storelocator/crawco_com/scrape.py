import csv

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://locator.crawco.com/api/countries/?callback=JSON_CALLBACK"
    domain = "crawco.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    all_countries = session.get(start_url, headers=hdr).json()
    for country in all_countries:
        country = country["code"]
        url = f"https://locator.crawco.com/api/cities/?country={country}&callback=JSON_CALLBACK"
        all_cities = session.get(url).json()
        for city in all_cities:
            if city.get("city"):
                city = city["city"]
                url = f"https://locator.crawco.com/api/branches/?country={country}&city={city}&callback=JSON_CALLBACK"
                all_locations += session.get(url).json()
            else:
                state = city["state"]
                url = f"https://locator.crawco.com/api/branches/?country={country}&state={state}&callback=JSON_CALLBACK"
                all_cities = session.get(url).json()
                for city in all_cities:
                    city = city["city"]
                    url = f"https://locator.crawco.com/api/branches/?country={country}&state={state}&city={city}&callback=JSON_CALLBACK"
                    all_locations += session.get(url).json()

    for poi in all_locations:
        store_url = f'https://www.crawco.com/about/our-locations/{poi["number"]}{poi["addressNum"]}'
        location_name = poi["name"]
        street_address = poi["address"].get("line1")
        if not street_address:
            street_address = poi["address"].get("line3")
        if street_address and poi["address"].get("line2"):
            street_address += " " + poi["address"]["line2"]
        if not street_address:
            street_address = poi["mailing"].get("line1")
            if poi["mailing"].get("line2"):
                street_address += " " + poi["mailing"]["line2"]
        if not street_address:
            street_address = "<MISSING>"
        city = poi["address"]["city"]
        state = poi["address"].get("state")
        state = state if state else "<MISSING>"
        zip_code = poi["address"].get("postal")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["number"]
        phone = poi["contact"].get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["mapping"]["lat"]
        longitude = poi["mapping"]["lng"]
        hours_of_operation = "<MISSING>"

        item = [
            domain,
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
