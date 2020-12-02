import csv
import json

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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "sasshoes.com"
    start_urls = [
        "https://www.sasshoes.com/on/demandware.store/Sites-sas-Site/en_US/Stores-GetNearestStores?34.07018&longitude=-118.399956&countryCode=US&distanceUnit=mi&maxdistance=50000&storeType=&assortment=",
        "https://www.sasshoes.com/on/demandware.store/Sites-sas-Site/en_US/Stores-GetNearestStores?latitude=34.07018&longitude=-118.399956&countryCode=US&distanceUnit=mi&maxdistance=50000&storeType=&assortment=",
        "https://www.sasshoes.com/on/demandware.store/Sites-sas-Site/en_US/Stores-GetNearestStores?latitude=34.07018&longitude=-118.399956&countryCode=CA&distanceUnit=mi&maxdistance=50000&storeType=&assortment=",
    ]

    all_poi = []
    for url in start_urls:
        response = session.get(url)
        data = json.loads(response.text)
        for elem in data["stores"].values():
            all_poi.append(elem)

    for poi in all_poi:
        store_url = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["stateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = ""
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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

        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
