import csv
import sgrequests
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
    locator_domain = "https://www.roots.com/"
    missingString = "<MISSING>"

    def r(l):
        return sgrequests.SgRequests().get(l)

    def fetch():
        a = r(
            "https://www.roots.com/on/demandware.store/Sites-RootsCA-Site/en_CA/Stores-Calculate?latlng=45.5005%2C-73.5684&within=1000000&storeFilters="
        )
        j = json.loads(a.text)
        return j

    s = fetch()

    result = []

    for e in s:
        result.append(
            [
                locator_domain,
                e["store_url"],
                e["name"],
                e["address1"] + " " + e["address2"],
                e["city"],
                e["stateCode"],
                e["postalCode"],
                e["countryCode"],
                e["ID"],
                e["phone"],
                missingString,
                e["latitude"],
                e["longitude"],
                e["storeHours"],
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
