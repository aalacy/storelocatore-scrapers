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
    scraped_items = []

    DOMAIN = "hugoboss.com"
    start_url = "https://production-na01-hugoboss.demandware.net/s/US/dw/shop/v16_9/stores?client_id=871c988f-3549-4d76-b200-8e33df5b45ba&latitude=36.18382034838561&longitude=-95.71289100000001&count=100&maxDistance=3670.4097048657495&distanceUnit=mi&start=0"

    all_locations = []
    response = session.get(start_url)
    data = json.loads(response.text)
    all_locations += data["data"]
    next_page = data["next"]
    while next_page:
        response = session.get(next_page)
        data = json.loads(response.text)
        all_locations += data["data"]
        next_page = data.get("next")

    for poi in all_locations:
        poi_url = "https://www.hugoboss.com/us/storedetail?storeid={}".format(poi["id"])
        poi_name = poi["name"]
        poi_name = poi_name if poi_name else "<MISSING>"
        street = poi.get("address1")
        street = street if street else "<MISSING>"
        city = poi.get("city")
        city = city if city else "<MISSING>"
        state = poi.get("state_code")
        state = state if state else "<MISSING>"
        zip_code = poi.get("postal_code")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi.get("country_code")
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["US", "CA"]:
            continue
        poi_number = poi["id"]
        poi_number = poi_number if poi_number else "<MISSING>"
        phone = poi.get("phone")
        phone = phone if phone else "<MISSING>"
        poi_type = poi["_type"]
        poi_type = poi_type if poi_type else "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = []
        if poi.get("store_hours"):
            hours_data = json.loads(poi["store_hours"])
            wd = {
                "1": "Monday",
                "2": "Thusday",
                "3": "Wendsday",
                "4": "Thursday",
                "5": "Friday",
                "6": "Saturday",
                "7": "Sunday",
            }
            for key, hours in hours_data.items():
                day = wd[key]
                opens = hours[0]
                closes = hours[1]
                hoo.append(f"{day} {opens} - {closes}")
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
        if poi_number not in scraped_items:
            scraped_items.append(poi_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
