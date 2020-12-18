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
    url = "https://www.lids.ca/api/stores?lat=43.7353011&long=-79.3291284&num=500&shipToStore=false"
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array:
        store = item["storeId"]
        name = item["name"]
        country = "CA"
        add = item["address1"]
        try:
            add = add + " " + item["address2"]
        except:
            pass
        add = add.strip()
        phone = item["phone"]
        website = "lids.ca"
        typ = item["storeBrand"]
        loc = "https://lids.ca" + item["untaggedURL"]
        city = item["city"]
        state = item["state"]
        zc = item["zip"]
        lat = item["latitude"]
        lng = item["longitude"]
        if " Lids" in add:
            add = add.split(" Lids")[0]
        hours = "Mon-Fri: " + item["monFriOpen"] + "-" + item["monFriClose"]
        hours = hours + "; Sat: " + item["satOpen"] + "-" + item["satClose"]
        hours = hours + "; Sun: " + item["sunOpen"] + "-" + item["sunClose"]
        if loc == "":
            loc = "<MISSING>"
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
