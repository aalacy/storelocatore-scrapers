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
    base_url = "https://www.poundland.co.uk"
    res = session.get(
        "https://www.poundland.co.uk/rest/poundland/V1/locator/?searchCriteria%5Bscope%5D=store-locator&searchCriteria%5Blatitude%5D=51.4810135&searchCriteria%5Blongitude%5D=-0.0082384&searchCriteria%5Bcurrent_page%5D=1&searchCriteria%5Bpage_size%5D=1000",
    )
    store_list = json.loads(res.text)["locations"]
    data = []
    for store in store_list:
        page_url = (
            "https://www.poundland.co.uk/store-finder/store_page/view/id/"
            + store["store_id"]
        )
        location_name = store["name"]
        street_address = (
            store["address"]["line"]
            if type(store["address"]["line"]) is str
            else " ".join(store["address"]["line"])
        )
        store_number = store["store_id"]
        city = store["address"]["city"]
        state = "<MISSING>"
        zip = store["address"]["postcode"]
        hours_of_operation = ""
        for x in store["opening_hours"]:
            hours_of_operation += x["day"] + ": " + x["hours"] + " "
        hours_of_operation = hours_of_operation.strip()
        country_code = store["address"]["country"]
        phone = store["tel"]
        location_type = store["type"]
        latitude = (
            "<MISSING>"
            if float(store["geolocation"]["latitude"]) == 0
            else store["geolocation"]["latitude"]
        )
        longitude = (
            "<MISSING>"
            if float(store["geolocation"]["longitude"]) == 0
            else store["geolocation"]["longitude"]
        )
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
                '="' + phone + '"',
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
