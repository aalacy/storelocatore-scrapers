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
    locator_domain = "https://kimscstores.com/"
    missingString = "<MISSING>"

    def r(l):
        return sgrequests.SgRequests().get(l)

    def fetch():
        a = r(
            "https://kimscstores.com/wp-admin/admin-ajax.php?action=store_search&lat=31.762115&lng=-95.630789&max_results=1000&search_radius=1000&autoload=1"
        )
        j = json.loads(a.text)
        return j

    s = fetch()

    result = []

    for e in s:
        h = e["hours"]
        if h == "":
            h = missingString
        result.append(
            [
                locator_domain,
                e["url"],
                missingString,
                e["address"] + " " + e["address2"],
                e["city"],
                e["state"],
                e["zip"],
                e["country"],
                e["id"],
                e["phone"],
                missingString,
                e["lat"],
                e["lng"],
                h,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
