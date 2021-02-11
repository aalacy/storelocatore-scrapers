import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://www.becn.com/api/store-locations?facets=&lat=50&long=-95&range=10000"
    r = session.get(url, headers=headers)
    country = "CA"
    website = "beacon-canada.com"
    loc = "<MISSING>"
    for item in json.loads(r.content)["items"]:
        name = item["storeLocation"]["name"]
        typ = item["storeLocation"]["branchname"]
        add = item["storeLocation"]["addressLine1"]
        add = add + " " + item["storeLocation"]["addressLine2"]
        add = add.strip()
        lat = item["storeLocation"]["latitude"]
        lng = item["storeLocation"]["longitude"]
        state = item["storeLocation"]["state"]
        hours = "<MISSING>"
        city = item["storeLocation"]["city"]
        phone = item["storeLocation"]["phone"]
        zc = item["storeLocation"]["postalcode"]
        store = "<MISSING>"
        if item["storeLocation"]["country"] == "CANADA":
            yield [
                website,
                loc,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
