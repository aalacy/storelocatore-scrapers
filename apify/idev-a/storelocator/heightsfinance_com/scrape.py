import csv
import json
from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    base_url = "https://www.heightsfinance.com/"
    data = []

    api_urls = [
        "https://www.heightsfinance.com/wp-json/wp/v2/loan_office_location?_fields=acf,slug&per_page=100&page=1",
        "https://www.heightsfinance.com/wp-json/wp/v2/loan_office_location?_fields=acf,slug&per_page=100&page=2",
    ]

    for api_url in api_urls:
        r = session.get(api_url)
        store_list = json.loads(r.text)

        for store in store_list:

            location_name = store["slug"]
            page_url = (
                "https://www.heightsfinance.com/loan-office-location/" + location_name
            )
            street_address = (
                store["acf"]["branch_address_1"] + store["acf"]["branch_address_2"]
            )
            store_number = store["acf"]["branch_id"]
            hours_of_operation = store["acf"]["branch_normal_hours"].replace(
                "<br />\r\n", " "
            )

            hours_of_operation = hours_of_operation.replace("<br />", "")
            city = store["acf"]["branch_city"]
            state = store["acf"]["branch_state"]
            zip = store["acf"]["branch_zip"]
            country_code = "US"
            phone = store["acf"]["branch_phone_number"]
            location_type = "<MISSING>"
            latitude = store["acf"]["branch_latitude"]
            longitude = store["acf"]["branch_longitude"]
            if "close" in store["acf"]["branch_special_hours"]:
                hours_of_operation += " (Temporarily closed)"

            data.append(
                [
                    base_url,
                    page_url,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
