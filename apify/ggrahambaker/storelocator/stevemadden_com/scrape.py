import csv
import json

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }

    locator_domain = "https://www.stevemadden.com/"
    url = "https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=stevemadden.myshopify.com&latitude=47.6338217&longitude=-122.3215448&max_distance=100000&limit=1000&calc_distance=1"
    r = session.get(url, headers=headers)

    loc_json = json.loads(r.content)

    found = []
    all_store_data = []
    for loc in loc_json["stores"]:

        country_code = loc["country"]
        if "US" not in country_code and "CA" not in country_code:
            continue

        location_name = loc["name"]
        if location_name in found:
            continue
        found.append(location_name)
        street_address = loc["address"].replace(", New York, NY 10028", "")
        if loc["address2"] != "NULL":
            street_address += " " + loc["address2"]

        city = loc["city"]
        state = loc["prov_state"]
        if not state:
            state = "<MISSING>"
        zip_code = loc["postal_zip"]
        if zip_code == "":
            zip_code = "<MISSING>"
        if len(zip_code) < 5:
            zip_code = "0" + zip_code
        phone_number = loc["phone"].split("/")[0].strip()
        if phone_number in found:
            continue
        found.append(phone_number)
        if phone_number == "":
            phone_number = "<MISSING>"

        lat = loc["lat"]
        longit = loc["lng"]

        hours = loc["hours"].replace("\r\n", " ").replace("  ", " ").strip()
        if hours == "NULL" or hours == "":
            hours = "<MISSING>"

        page_url = "<MISSING>"

        store_number = loc["store_id"]
        location_type = "<MISSING>"

        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]

        all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
