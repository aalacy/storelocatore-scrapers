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

    DOMAIN = "hometownpet.com"
    start_url = "https://rebase.global.ssl.fastly.net/api/places/index.json?api_key=ab770520133faf5ce0c905bdacb4d05f&lat=36.059&lng=-86.671"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["locations"]:
        poi_name = poi["info"]["name"]
        poi_url = "<MISSING>"
        street = poi["info"]["location"]["street"]
        if poi["info"]["location"]["street_2"]:
            street += " " + poi["info"]["location"]["street_2"]
        street = street if street else "<MISSING>"
        city = poi["info"]["location"]["city"]
        city = city if city else "<MISSING>"
        state = poi["info"]["location"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["info"]["location"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["info"]["location"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        poi_number = poi["id"]
        poi_number = poi_number if poi_number else "<MISSING>"
        phone = poi["info"]["phone"]
        phone = phone if phone else "<MISSING>"
        poi_type = "<MISSING>"
        poi_type = poi_type if poi_type else "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = []
        if poi["info"].get("hours"):
            hoo_dict = {}
            for day_raw, hours in poi["info"]["hours"].items():
                day = day_raw.split("_")[0]
                if "open" in day_raw:
                    if hoo_dict.get(day):
                        hoo_dict[day]["opens"] = hours
                    else:
                        hoo_dict[day] = {}
                        hoo_dict[day]["opens"] = hours
                else:
                    if hoo_dict.get(day):
                        hoo_dict[day]["closes"] = hours
                    else:
                        hoo_dict[day] = {}
                        hoo_dict[day]["closes"] = hours
            for day, hours in hoo_dict.items():
                opens = hours["opens"]
                closes = hours["closes"]
                hoo.append(f"{day} {opens} {closes}")
        hoo = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
