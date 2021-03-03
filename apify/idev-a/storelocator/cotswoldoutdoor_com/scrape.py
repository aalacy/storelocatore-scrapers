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
    base_url = "https://www.cotswoldoutdoor.com"
    res = session.get(
        "https://www.cotswoldoutdoor.com/api/services/public/store/cotswold/en",
    )
    store_list = json.loads(res.text)
    data = []

    for store in store_list:
        location_name = store["name"]
        store_number = store["code"]
        city = store["city"]
        state = "<MISSING>"
        page_url = "https://www.cotswoldoutdoor.com/stores/" + store["alias"] + ".html"
        street_address = store["street"]
        zip = store["postalcode"]
        country_code = store["country"]
        if country_code != "GB":
            continue
        phone = store["phoneNumber"]
        location_type = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours = store["dailyOpeningHours"][0]
        hours_of_operation = ""
        for x in hours:
            hours_of_operation += (
                x["day"]
                + ": "
                + (
                    "Closed"
                    if x["open"] == 0
                    else x["openTimeLabel"] + "-" + x["closeTimeInMinutes"]
                )
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
