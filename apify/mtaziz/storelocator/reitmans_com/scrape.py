from sgrequests import SgRequests
from sglogging import SgLogSetup
import csv
import json

logger = SgLogSetup().get_logger(logger_name="reitmans_com")


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


def generate_ids():
    comma = "%2C"
    start_num = 2615832
    end_num = ""
    total_ids_to_be_crawled = 300
    end_num = start_num + total_ids_to_be_crawled
    ids_list = []
    for i in range(start_num, end_num):
        ids_list.append(str(i))
    return f"{comma}".join(ids_list)


def fetch_data():
    # Your scraper here
    ids_list_300 = (
        generate_ids()
    )  # We would try with 300 ids so that existing store count of 245 would match and cover any forward-looking stores to be added
    session = SgRequests()
    items = []
    DOMAIN = "reitmans.com"
    start_url_new = f"https://sls-api-service.sweetiq-sls-production-west.sweetiq.com/hUbqnBs8QgNLa3E99wFoijIgZh0cyh/locations-details?locale=en_CA&ids={ids_list_300}&clientId=585950d3d10a87d03310f605&cname=locations.reitmans.com"
    headers_new = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }

    response = session.get(start_url_new, headers=headers_new)
    data = json.loads(response.text)

    for poi in data["features"]:
        store_url = "https://locations.reitmans.com/" + poi["properties"]["slug"]
        location_name = poi["properties"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["properties"]["addressLine1"]
        if poi["properties"]["addressLine2"]:
            street_address += ", " + poi["properties"]["addressLine2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["properties"]["city"]
        city = city if city else "<MISSING>"
        state = poi["properties"]["province"]
        state = state if state else "<MISSING>"
        zip_code = poi["properties"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["properties"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["properties"]["branch"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["properties"]["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["geometry"]["coordinates"][-1]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geometry"]["coordinates"][0]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["properties"]["hoursOfOperation"].items():
            if hours:
                hours_of_operation.append(
                    "{} {} - {}".format(day, hours[0][0], hours[0][1])
                )
            else:
                hours_of_operation.append("{} closed".format(day))
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        if state.isnumeric():
            new_state = zip_code
            zip_code = state
            state = new_state

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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    logger.info(f"[Scraping Finished | Total Stores Count: {len(data)}]")
    write_output(data)


if __name__ == "__main__":
    scrape()
