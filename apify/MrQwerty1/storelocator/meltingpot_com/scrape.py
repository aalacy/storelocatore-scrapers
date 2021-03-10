import csv
import json

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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
    out = []
    locator_domain = "https://www.meltingpot.com/"
    api_url = "https://www.meltingpot.com/files/2777/widget287448.js"

    session = SgRequests()
    r = session.get(api_url)
    text = r.text
    text = text.replace("widget287448DataCallback(", "").replace(");", "")
    js = json.loads(text)["PropertyorInterestPoint"]

    for j in js:
        location_name = j.get("interestpointpropertyname") or "<MISSING>"
        street_address = j.get("interestpointpropertyaddress") or "<MISSING>"
        city = j.get("interestpointCity") or "<MISSING>"
        if city.find("-") != -1:
            city = city.split("-")[0].strip()
        elif city.find(",") != -1:
            city = city.split(",")[0].strip()
        state = j.get("interestpointState") or "<MISSING>"
        postal = j.get("interestpointPostalCode") or "<MISSING>"
        country_code = "US"
        if len(postal) > 5:
            country_code = "CA"
        store_number = (
            j.get("interestpointPropertyRestaurantInformationWidgetJSONFeedURL").split(
                "/"
            )[-2]
            if j.get("interestpointPropertyRestaurantInformationWidgetJSONFeedURL")
            else "<MISSING>"
        )
        page_url = j.get("interestpointMoreInfoLink") or "<MISSING>"
        phone = j.get("interestpointPhoneNumber") or "<MISSING>"
        latitude = j.get("interestpointinterestlatitude") or "<MISSING>"
        longitude = j.get("interestpointinterestlongitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<INACCESSIBLE>"

        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
