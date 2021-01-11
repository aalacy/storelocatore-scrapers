import re
import csv
import json

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    session = SgRequests()

    items = []

    DOMAIN = "costavida.com"
    start_url = "https://www.costavida.com/actions/costa-vida-locations-module/location/get-locations"
    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get("https://www.costavida.com/locations")
    token = re.findall('csrfTokenValue = "(.+)";', response.text)[0]
    formdata = {"CRAFT_CSRF_TOKEN": token}

    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://www.costavida.com/locations/{}".format(poi["slug"])
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["zipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]["label"]
        if country_code == "Select a Country":
            country_code = "<MISSING>"
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeId"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednsday",
            "Thursday",
            "Friday",
            "Satarday",
        ]
        hours = []
        for elem in poi["hours"].values():
            if elem["open"]:
                opens = elem["open"]["date"].split()[-1].split(":00.")[0]
                closes = elem["close"]["date"].split()[-1].split(":00.")[0]
                hours.append(f"{opens} - {closes}")
            else:
                hours.append("Closed")
        hours_of_operation = list(map(lambda day, hour: day + " " + hour, days, hours))
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
