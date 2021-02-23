import csv
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    data = []
    url = "https://www.goodygoody.com/ccstoreui/v1/products?q=(type%20eq%20%22Store%22)"

    r = session.get(url, headers=headers, verify=False)
    loclist = json.loads(r.text)
    loclist = loclist["items"]
    for loc in loclist:
        title = loc["storeName"]
        sublink = "https://www.goodygoody.com" + loc["route"]
        store = loc["id"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        street = loc["addressLine1"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zipcode"]
        ccode = loc["countryCode"]
        store_type = loc["type"]
        phone = loc["phone1"]
        if title == "":
            title = "<MISSING>"
        if store == "":
            store = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if longt == "":
            longt = "<MISSING>"
        if street == "":
            street = "<MISSING>"
        if city == "":
            city = "<MISSING>"
        if pcode == "":
            pcode = "<MISSING>"
        if ccode == "":
            ccode = "UK"
        if store_type == "":
            store_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        data.append(
            [
                "https://www.goodygoody.com",
                sublink,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                store_type,
                lat,
                longt,
                hours_of_operation,
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
