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
    locator_domain = "https://www.ladyjanes.com/"
    api = "https://www.ladyjanes.com/location/getLocationsBySearch"
    missingString = "<MISSING>"

    p = {"search": "48083"}

    s = SgRequests()

    locs = json.loads(s.post(api, data=p).text)["data"]["visibleLocations"]
    result = []
    for loc in locs:
        st = locs[loc]
        if st["wait_time"] == "Coming Soon":
            pass
        else:
            store_name = st["api"]["name"]
            address = st["street_address"]
            state = st["state"]
            city = st["city"]
            store_zip = st["api"]["address"].split(" ")[-1]
            lat = st["api"]["lat"]
            lng = st["api"]["lng"]
            store_number = st["id"]
            phone = st["phone"]
            hours = (
                "Monday-Thursday : {}, Friday : {}, Saturday : {}, Sunday : {}".format(
                    st["monday_thursday"], st["friday"], st["saturday"], st["sunday"]
                )
            )
            result.append(
                [
                    locator_domain,
                    missingString,
                    store_name,
                    address,
                    city,
                    state,
                    store_zip,
                    missingString,
                    store_number,
                    phone,
                    missingString,
                    lat,
                    lng,
                    hours,
                ]
            )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
