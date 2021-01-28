import csv
from sgrequests import SgRequests
import json


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
    # Your scraper here
    locator_domain = "https://www.rentawheel.com/"
    api = "https://www.rentawheel.com/retailers.php"
    missingString = "<MISSING>"

    s = SgRequests()
    api = s.get(api).text

    apiJSON = json.loads(api)

    result = []

    for el in apiJSON:
        if not el["hours"]:
            result.append(
                [
                    locator_domain,
                    missingString,
                    el["title"],
                    missingString,
                    el["city"],
                    el["state"],
                    el["zip"],
                    missingString,
                    el["storenumber"],
                    el["phone"],
                    el["phone"],
                    el["lat"],
                    el["lng"],
                    missingString,
                ]
            )
        elif not el["address"]:
            result.append(
                [
                    locator_domain,
                    missingString,
                    el["title"],
                    missingString,
                    el["city"],
                    el["state"],
                    el["zip"],
                    missingString,
                    el["storenumber"],
                    el["phone"],
                    el["phone"],
                    el["lat"],
                    el["lng"],
                    el["hours"]
                    .replace("M", "Monday")
                    .replace("F", "Friday")
                    .replace("/", ",")
                    .replace("SAT", "Saturday")
                    .strip(),
                ]
            )
        elif el["phone"] == "Coming Soon!":
            result.append(
                [
                    locator_domain,
                    missingString,
                    el["title"],
                    missingString,
                    el["city"],
                    el["state"],
                    el["zip"],
                    missingString,
                    el["storenumber"],
                    el["phone"],
                    el["phone"],
                    el["lat"],
                    el["lng"],
                    el["hours"]
                    .replace("M", "Monday")
                    .replace("F", "Friday")
                    .replace("/", ",")
                    .replace("SAT", "Saturday")
                    .strip(),
                ]
            )
        else:
            result.append(
                [
                    locator_domain,
                    missingString,
                    el["title"],
                    el["address"],
                    el["city"],
                    el["state"],
                    el["zip"],
                    missingString,
                    el["storenumber"],
                    el["phone"],
                    missingString,
                    el["lat"],
                    el["lng"],
                    el["hours"]
                    .replace("M", "Monday")
                    .replace("F", "Friday")
                    .replace("/", ",")
                    .replace("SAT", "Saturday")
                    .strip(),
                ]
            )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
