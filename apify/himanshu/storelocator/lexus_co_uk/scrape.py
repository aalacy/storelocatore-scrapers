import csv
from sgrequests import SgRequests

session = SgRequests()


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
    items = []
    scraped_items = []

    start_url = "https://www.lexus.co.uk/api/dealers/all"
    domain = "lexus.co.uk"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    response = session.get(start_url, headers=headers).json()
    all_locations = response["dealers"]

    for poi in all_locations:
        store_url = poi.get("url")
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["address1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region"]
        state = state.strip() if state else "<MISSING>"
        if state.isdigit():
            state = "<MISSING>"
        zip_code = poi["address"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["address"].get("geo"):
            latitude = poi["address"]["geo"]["lat"]
            longitude = poi["address"]["geo"]["lon"]
        hoo = []
        if poi["openingTimes"]:
            if poi["openingTimes"].get("WorkShop"):
                for elem in poi["openingTimes"]["WorkShop"]:
                    day = elem["day"]
                    if elem["slots"]:
                        opens = elem["slots"][0]["openFrom"]
                        closes = elem["slots"][0]["openTo"]
                        hoo.append(f"{day} {opens} {closes}")
                    else:
                        hoo.append(f"{day} closed")
            else:
                for elem in poi["openingTimes"]["ShowRoom"]:
                    day = elem["day"]
                    if elem["slots"]:
                        opens = elem["slots"][0]["openFrom"]
                        closes = elem["slots"][0]["openTo"]
                        hoo.append(f"{day} {opens} {closes}")
                    else:
                        hoo.append(f"{day} closed")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
